import os
import shutil

def export_post_kit(
    piece_id: str, 
    brand_id: str, 
    caption: str, 
    asset_urls: list, 
    alt_texts: list, 
    first_comment: str = "", 
    channel: str = "instagram"
) -> str:
    """
    Implements §12.3.1 (Manual Handoff Bundle).
    Creates a per-piece folder containing the Post Kit.
    """
    handoff_dir = os.path.join(os.getcwd(), "brands", brand_id, "handoff", piece_id)
    os.makedirs(handoff_dir, exist_ok=True)
    
    # In a real system, we download the actual asset bytes. Here we mock image files or copy if local.
    for i, asset in enumerate(asset_urls):
        asset_file = os.path.join(handoff_dir, f"{str(i+1).zfill(2)}.jpg")
        with open(asset_file, "w") as f:
            f.write(f"Mock image content for {asset}")
            
    # Caption and copy blocks
    caption_file = os.path.join(handoff_dir, "caption.txt")
    with open(caption_file, "w", encoding="utf-8") as f:
        # Add a warning if first line exceeds typical preview length
        first_line = caption.split('\n')[0]
        if len(first_line) > 125:
            f.write("WARNING: First line will truncate behind '... more'\n\n")
        f.write(caption)
        
    if first_comment:
        first_comment_file = os.path.join(handoff_dir, "first_comment.txt")
        with open(first_comment_file, "w", encoding="utf-8") as f:
            f.write(first_comment)
            
    # Alt texts per slide
    alt_text_file = os.path.join(handoff_dir, "alt_texts.txt")
    with open(alt_text_file, "w", encoding="utf-8") as f:
        for i, alt in enumerate(alt_texts):
            f.write(f"Slide {str(i+1).zfill(2)}: {alt}\n")
            
    # Checklist
    checklist_file = os.path.join(handoff_dir, "checklist.txt")
    checklist_content = """1. Upload images in order (01-0N)
2. Paste caption
3. Add per-slide alt text (Advanced -> alt text)
4. Publish
5. Paste first-comment hashtags (if any)
6. Return to Agent Atelier and 'Mark posted'"""
    with open(checklist_file, "w", encoding="utf-8") as f:
        f.write(checklist_content)
        
    return handoff_dir
