#!/usr/bin/env python3
"""caption.py — composite an advertising-grade caption onto an image.

Usage:
  caption.py <in> <out> "Headline" [--font serifbold] [--theme dark|light]
     [--accent "#E8A33D"] [--align left|center] [--size 0] [--kicker "LABEL"]
     [--wordmark "Art of Living · Ludhiana"]

Brand type system (consistent across the feed): a large serif headline with a
short accent rule, an optional small-caps kicker, and an optional small-caps
wordmark pinned to the bottom. The IMAGE varies post to post; THIS type system
does not. Image model renders NO text — all type is designed here.

Themes: 'dark' = bottom gradient scrim + near-white text (for dark photos);
        'light' = no scrim + dark warm text (for photos with a light lower band).
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

FONTS = {
    "serif":     ("/System/Library/Fonts/Supplemental/Georgia.ttf", 0),
    "serifbold": ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", 0),
    "didot":     ("/System/Library/Fonts/Supplemental/Didot.ttc", 1),
    "sans":      ("/System/Library/Fonts/Supplemental/Futura.ttc", 0),
}
SMALL_FONT = ("/System/Library/Fonts/Supplemental/Futura.ttc", 0)

def load_font(key, size):
    path, idx = FONTS.get(key, FONTS["serifbold"])
    try: return ImageFont.truetype(path, size, index=idx)
    except Exception: return ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", size)

def small(size):
    try: return ImageFont.truetype(SMALL_FONT[0], size, index=SMALL_FONT[1])
    except Exception: return ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", size)

def spaced(s, n=2):  # letter-spacing for small caps
    return (" " * n).join(list(s.upper()))

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("text")
    ap.add_argument("--font", default="serifbold")
    ap.add_argument("--theme", default="dark", choices=["dark", "light"])
    ap.add_argument("--accent", default="")
    ap.add_argument("--align", default="left")
    ap.add_argument("--size", type=int, default=0)
    ap.add_argument("--kicker", default="")
    ap.add_argument("--wordmark", default="")
    ap.add_argument("--logo", default="")
    ap.add_argument("--logotext", default="Ludhiana")
    ap.add_argument("--action", default="")   # CTA line for outro slides (below headline)
    ap.add_argument("--subhead", default="")  # wrapped sub-line under the headline (NOT the kicker)
    a = ap.parse_args()

    light = a.theme == "light"
    text_col = (38, 30, 22, 255) if light else (255, 252, 247, 255)
    accent = a.accent or ("#B8800E" if light else "#F2C12E")  # AoL gold-yellow (gradient's gold end) — more readable than saffron; logo itself stays saffron
    shadow = None if light else (0, 0, 0, 150)

    img = Image.open(a.inp).convert("RGB")
    W, H = img.size
    margin = int(W * 0.075)
    max_w = W - 2 * margin
    size = a.size or int(W * 0.072)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    font = load_font(a.font, size)
    lines = wrap(d, a.text, font, max_w)
    while len(lines) > 3 and size > 30:
        size -= 4; font = load_font(a.font, size); lines = wrap(d, a.text, font, max_w)

    asc, desc = font.getmetrics()
    lh = int((asc + desc) * 1.06)
    block_h = lh * len(lines)
    sub_font = small(int(W * 0.027)) if a.subhead else None
    sub_lines = wrap(d, a.subhead, sub_font, max_w) if a.subhead else []
    sub_lh = int(sum(sub_font.getmetrics()) * 1.14) if a.subhead else 0
    subhead_h = (sub_lh * len(sub_lines) + int(H * 0.014)) if a.subhead else 0
    wm_h = int(W * 0.12) if a.logo else (int(W * 0.05) if a.wordmark else 0)
    action_h = int(H * 0.060) if a.action else 0
    bottom_pad = int(H * 0.055) + wm_h + action_h + subhead_h
    top_of_text = H - bottom_pad - block_h
    accent_gap = int(W * 0.022)
    kick_h = int(W * 0.05) if a.kicker else 0
    scrim_top = max(0, top_of_text - kick_h - accent_gap - int(H * 0.10))

    # scrim — a feathered band that reaches FULL strength by the top of the text
    # region and holds to the bottom, so type reads even over a BRIGHT photo
    # (CD root-cause fix: the old dark gradient washed out on bright skies).
    grad = Image.new("L", (1, H), 0)
    feather = max(1, int(H * 0.10)); full_at = scrim_top + feather
    cap_alpha = 242 if light else 224
    col = (250, 246, 239, 255) if light else (8, 7, 11, 255)
    for yy in range(H):
        if yy < scrim_top: v = 0
        elif yy < full_at: v = int(((yy - scrim_top) / feather) * cap_alpha)
        else: v = cap_alpha
        grad.putpixel((0, yy), v)
    grad = grad.resize((W, H))
    sc = Image.new("RGBA", (W, H), col); sc.putalpha(grad)
    layer = Image.alpha_composite(layer, sc); d = ImageDraw.Draw(layer)

    x_left = margin
    # kicker — auto-fit so it can NEVER run off the frame (CD fix). Shrink, then
    # drop letter-spacing, then drop case-spacing, until it fits one line.
    if a.kicker:
        ksz = int(W * 0.026); kf = small(ksz); ks = spaced(a.kicker)
        while d.textlength(ks, font=kf) > max_w and ksz > 12:
            ksz -= 1; kf = small(ksz)
        if d.textlength(ks, font=kf) > max_w: ks = spaced(a.kicker, 1)
        if d.textlength(ks, font=kf) > max_w: ks = a.kicker.upper()
        ky = top_of_text - accent_gap - kick_h
        kx = x_left if a.align == "left" else (W - d.textlength(ks, font=kf)) // 2
        d.text((kx, ky), ks, font=kf, fill=accent)
    # accent rule
    ry = top_of_text - accent_gap
    rule_w = int(W * 0.085); rule_h = max(3, int(W * 0.006))
    rx = x_left if a.align == "left" else (W - rule_w) // 2
    d.rectangle([rx, ry, rx + rule_w, ry + rule_h], fill=accent)
    # headline
    y = top_of_text
    for ln in lines:
        lx = x_left if a.align == "left" else (W - d.textlength(ln, font=font)) // 2
        if shadow: d.text((lx + 2, y + 3), ln, font=font, fill=shadow)
        d.text((lx, y), ln, font=font, fill=text_col)
        y += lh
    # subhead (wrapped) — small line under the headline; the proper home for a
    # sub-line (NOT the kicker, which clips). Sits on the same scrim, so it reads.
    if sub_lines:
        sy = y + int(H * 0.012)
        for sl in sub_lines:
            sx = x_left if a.align == "left" else (W - d.textlength(sl, font=sub_font)) // 2
            d.text((sx, sy), sl, font=sub_font, fill=text_col)
            sy += sub_lh
        y = sy
    # CTA action line (outro slides) — small, below the headline/subhead; auto-fit.
    if a.action:
        asz = int(W * 0.0205); af = small(asz); act = a.action
        while d.textlength(act, font=af) > max_w and asz > 11:
            asz -= 1; af = small(asz)
        ay = y + int(H * 0.020)
        ax = x_left if a.align == "left" else (W - d.textlength(act, font=af)) // 2
        d.text((ax, ay), act, font=af, fill=accent)

    # brandmark pinned bottom-centre: official Art of Living logo + "Ludhiana"
    if a.logo:
        try:
            logo = Image.open(a.logo).convert("RGBA")
            th = max(40, int(H * 0.075)); s2 = th / logo.height
            logo = logo.resize((max(1, int(logo.width * s2)), th))
            if not light:  # recolour the dark wordmark text to cream so it reads on a dark scrim
                lp = logo.load()
                for yy in range(logo.height):
                    for xx in range(logo.width):
                        r, g, b, al = lp[xx, yy]
                        if al > 30 and r < 85 and g < 75 and b < 85:
                            lp[xx, yy] = (248, 244, 237, al)
            lf = small(int(W * 0.019)); lt = spaced(a.logotext, 2)
            ltw = d.textlength(lt, font=lf); cx = W // 2
            logo_y = H - int(H * 0.135)
            layer.alpha_composite(logo, (cx - logo.width // 2, logo_y))
            d.text((cx - ltw // 2, logo_y + logo.height + int(H * 0.013)), lt, font=lf, fill=accent)
        except Exception as e:
            print("logo composite failed:", e)
    elif a.wordmark:
        wf = small(int(W * 0.0225)); ws = spaced(a.wordmark, 1)
        wy = H - int(H * 0.045)
        wx = x_left if a.align == "left" else (W - d.textlength(ws, font=wf)) // 2
        d.text((wx, wy), ws, font=wf, fill=accent)

    out = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    out.save(a.out, quality=95)
    print("WROTE", a.out, "| theme", a.theme, "| lines", len(lines), "| size", size)

if __name__ == "__main__":
    main()
