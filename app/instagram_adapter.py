def instagram_publish(piece_id: str, image_urls: list, caption: str, first_comment: str = "") -> dict:
    """
    Implements the explicitly absent Instagram adapter.
    Surfaces "won't auto-publish — hand off by hand" when called.
    """
    # The P5-A contract states the adapter is explicitly ABSENT for today.
    # An approved piece on an adapterless channel surfaces as "won't auto-publish — hand off by hand", never a silent stall.
    raise NotImplementedError("won't auto-publish — hand off by hand")
