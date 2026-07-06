import os
import shutil
import urllib.request

# Magic-byte signatures: a Post Kit slide must be a real image, never a
# placeholder — a corrupt bundle that looks complete is a silent stall (§12.3.1).
_IMAGE_MAGIC = {
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG\r\n\x1a\n": ".png",
}


def _default_fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def _image_ext(data: bytes):
    for magic, ext in _IMAGE_MAGIC.items():
        if data.startswith(magic):
            return ext
    return None


def export_post_kit(
    piece_id: str,
    brand_id: str,
    caption: str,
    asset_urls: list,
    alt_texts: list,
    first_comment: str = "",
    channel: str = "instagram",
    fetch=_default_fetch,
) -> str:
    """
    Implements §12.3.1 (Manual Handoff Bundle).
    Creates a per-piece folder containing the Post Kit.

    Downloads the real asset bytes (or copies a local file) and validates the
    image magic bytes. A failed or non-image download writes a loud
    download_error_NN.txt + KIT_INCOMPLETE.txt marker — never a fake slide.
    """
    handoff_dir = os.path.join(os.getcwd(), "brands", brand_id, "handoff", piece_id)
    os.makedirs(handoff_dir, exist_ok=True)

    errors = []
    for i, asset in enumerate(asset_urls):
        idx = str(i + 1).zfill(2)
        try:
            if os.path.exists(asset):
                with open(asset, "rb") as f:
                    data = f.read()
            else:
                data = fetch(asset)
            ext = _image_ext(data)
            if ext is None:
                raise ValueError(
                    f"downloaded content is not a supported image (first bytes: {data[:12]!r})"
                )
            with open(os.path.join(handoff_dir, f"{idx}{ext}"), "wb") as f:
                f.write(data)
        except Exception as e:
            errors.append((asset, str(e)))
            with open(
                os.path.join(handoff_dir, f"download_error_{idx}.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(f"FAILED to fetch slide {idx}\nurl: {asset}\nerror: {e}\n")

    if errors:
        with open(
            os.path.join(handoff_dir, "KIT_INCOMPLETE.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(
                "This Post Kit is INCOMPLETE — one or more slides failed to download.\n"
                "Do NOT post from this bundle. See download_error_*.txt for details.\n"
            )
        print(f"[post_kit] WARNING: {piece_id} kit INCOMPLETE ({len(errors)} slide(s) failed)")

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
