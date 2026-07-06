import datetime
import argparse
import uuid

def evaluate_backpressure(
    queue_depth: int,
    days_since_last_owner_action: int,
    max_queue_depth: int = None,
    posts_per_week_target: int = 5,
    owner_absence_pause_days: int = 7
) -> bool:
    """
    Evaluates the §9.5 backpressure precondition.
    """
    effective_max_queue = max_queue_depth if max_queue_depth is not None else 2 * posts_per_week_target
    return queue_depth > effective_max_queue and days_since_last_owner_action >= owner_absence_pause_days

def compose_week(
    as_of: datetime.datetime,
    brand_kit: dict,
    active_campaigns: list,
    queue_depth: int,
    days_since_last_owner_action: int
) -> dict:
    """
    Monday-tick composition rule (Day 5 SDD; §9.5 intent → §13.1 Tasks)
    """
    brand_id = brand_kit.get('brand_short_name', 'BRAND').upper().replace(' ', '-')
    week_of = as_of.strftime("%Y-W%W")
    
    posts_per_week_target = brand_kit.get('posts_per_week_target', 5)
    max_queue_depth = brand_kit.get('max_queue_depth')
    owner_absence_pause_days = brand_kit.get('owner_absence_pause_days', 7)
    
    # Precondition: Backpressure
    is_paused = evaluate_backpressure(
        queue_depth, days_since_last_owner_action, max_queue_depth, posts_per_week_target, owner_absence_pause_days
    )
    
    campaign_overrides_bp = brand_kit.get('campaign_overrides_backpressure', False)
    
    # Base: standing_week
    standing_week = brand_kit.get('standing_week', {})
    quiet_days = set(brand_kit.get('quiet_days', []))
    blackout_dates = brand_kit.get('blackout_dates', []) # List of {name, dates}
    
    # Note: In a real implementation we would resolve blackout dates against as_of week.
    
    composed_tasks = []
    
    max_posts_per_week = brand_kit.get('max_posts_per_week', 6)
    campaign_max_posts = brand_kit.get('campaign_max_posts_per_week', 8)
    
    # Check active campaigns
    campaign_active = len(active_campaigns) > 0
    effective_max = campaign_max_posts if campaign_active else max_posts_per_week
    
    # Iterate through days
    days_order = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    
    # Add weekend slots if configured
    if 'weekend' in standing_week:
        standing_week['sat'] = standing_week.get('weekend')
        standing_week['sun'] = standing_week.get('weekend')
        
    slots_to_consider = []
    for day in days_order:
        if day in quiet_days:
            continue
            
        slot = standing_week.get(day)
        if not slot:
            continue
            
        if slot.get('track') == 'quiet':
            continue
            
        slots_to_consider.append({"day": day, "slot": slot})
        
    # Apply Campaign Overlay
    for campaign in active_campaigns:
        overlay_mode = campaign.get('overlay_mode', 'add')
        if overlay_mode == 'add':
            for c_slot in campaign.get('slots', []):
                slots_to_consider.append({"day": c_slot.get('day', 'mon'), "slot": c_slot, "campaign_id": campaign.get('id')})
        elif overlay_mode == 'replace':
            # Replace evergreen slots
            c_slots = campaign.get('slots', [])
            c_idx = 0
            for item in slots_to_consider:
                if item['slot'].get('track') == 'evergreen' and c_idx < len(c_slots):
                    item['slot'] = c_slots[c_idx]
                    item['campaign_id'] = campaign.get('id')
                    c_idx += 1
                    
    # Backpressure filtering
    final_slots = []
    research_min = brand_kit.get('research_post_min_per_week', 1)
    for item in slots_to_consider:
        if is_paused:
            # Drop routine tasks
            is_campaign = 'campaign_id' in item
            is_research = item['slot'].get('flag') == 'research_grounded'
            
            if not campaign_overrides_bp:
                continue # Pause means no tasks
            else:
                if not is_campaign and not (is_research and research_min > 0):
                    continue
        final_slots.append(item)
                    
    # Clamp to effective_max
    if len(final_slots) > effective_max:
        # Drop lowest-priority first: evergreen -> non-flagship offering
        # NEVER drop a research_grounded slot if research_post_min_per_week > 0
        final_slots.sort(key=lambda x: (
            1 if x['slot'].get('flag') == 'research_grounded' and research_min > 0 else 0,
            1 if x['slot'].get('track', '').startswith('offering:') else 0,
            0 # Evergreen is lowest
        ), reverse=True)
        final_slots = final_slots[:effective_max]
        
    # Emit tasks
    tasks = []
    for item in final_slots:
        slot = item['slot']
        track = slot.get('track', '')
        offering_id = track.split(':')[1] if track.startswith('offering:') else None
        
        task = {
            "id": str(uuid.uuid4()),
            "brand_id": brand_id,
            "week_of": week_of,
            "offering_id": offering_id,
            "language": slot.get('language', brand_kit.get('languages', ['en'])[0]),
            "flag": slot.get('flag'),
            "channel": slot.get('channel'),
            "format": slot.get('format', 'single'),
            "target_date": item['day'],
            "brand_kit_version": brand_kit.get('brand_kit_version', 1)
        }
        if 'campaign_id' in item:
            task['campaign_id'] = item['campaign_id']
            
        tasks.append(task)
        
    return {
        "status": "PAUSED" if is_paused else "ACTIVE",
        "week_of": week_of,
        "tasks": tasks,
        "audit_entry": {
            "action": "WEEK_PLAN_PAUSED" if is_paused else "WEEK_PLAN_COMPOSED",
            "target": f"{brand_id}#week:{week_of}",
            "timestamp": as_of.isoformat()
        } if is_paused else None
    }
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", type=str, required=True, help="ISO format datetime")
    args = parser.parse_args()
    
    as_of_dt = datetime.datetime.fromisoformat(args.as_of)
    print(f"Simulating Monday tick as of {as_of_dt.isoformat()}")
