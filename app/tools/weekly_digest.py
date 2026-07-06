import datetime

def generate_weekly_digest(
    shipped_pieces: list,
    queued_pieces: list,
    standing_week_slots: int,
    research_min: int,
    paused_routines: list,
    image_spend: float,
    tokens_used: int,
    cd_verdicts: int,
    owner_overrides: int,
    backpressure_active: bool,
    queue_depth: int,
    days_since_owner_action: int
) -> str:
    """
    Composes the weekly visibility digest.
    """
    digest = []
    digest.append("## Weekly Visibility Digest\n")
    
    # 1. What shipped
    shipped_count = len(shipped_pieces)
    digest.append(f"**What Shipped:** {shipped_count} pieces (Target: {standing_week_slots})")
    for p in shipped_pieces:
        digest.append(f"- [{p.get('piece_id')}] {p.get('channel')} | {p.get('track')} | {p.get('language')}")
    digest.append("")
        
    # 2. What's queued
    digest.append(f"**Approval Queue / CD Review:** {len(queued_pieces)} pieces")
    for p in queued_pieces:
        digest.append(f"- [{p.get('piece_id')}] Age: {p.get('age_days')} days - {p.get('link')}")
    digest.append("")
        
    # 3. Slots hit/missed
    missed_slots = standing_week_slots - shipped_count
    if missed_slots > 0:
        digest.append(f"**Slots Missed:** {missed_slots}")
    else:
        digest.append("**Slots Hit:** Target met or exceeded.")
    digest.append("")
        
    # 4. Research minimum
    if research_min > 0:
        research_shipped = sum(1 for p in shipped_pieces if p.get('flag') == 'research_grounded')
        if research_shipped >= research_min:
            digest.append(f"**Research Minimum:** Met ({research_shipped} >= {research_min})")
        else:
            digest.append(f"**Research Minimum:** MISSED ({research_shipped} < {research_min})")
        digest.append("")
        
    # 5. Paused routines / Backpressure
    digest.append("**Paused Routines / Pending Approvals:**")
    if backpressure_active:
        digest.append(f"> **BACKPRESSURE PAUSE ACTIVE** (Queue Depth: {queue_depth}, Days since owner action: {days_since_owner_action}). Any action resumes it.")
    if not paused_routines and not backpressure_active:
        digest.append("None.")
    else:
        for r in paused_routines:
            digest.append(f"- {r}")
    digest.append("")
    
    # 6. Spend
    digest.append(f"**Spend:** Image Generation: ${image_spend:.2f} | Tokens Used: {tokens_used}")
    digest.append("")
    
    # 7. CD <-> Owner Agreement Rate
    if cd_verdicts > 0:
        agreement_rate = ((cd_verdicts - owner_overrides) / cd_verdicts) * 100
        digest.append(f"**CD ↔ Owner Agreement Rate:** {agreement_rate:.1f}% ({owner_overrides} false-approves)")
    else:
        digest.append("**CD ↔ Owner Agreement Rate:** N/A (No verdicts this week)")
        
    return "\n".join(digest)
