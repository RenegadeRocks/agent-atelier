"""Record the Studio Floor console on REAL state, including the Approve click.

Starts floor_serve on :8787, opens the console in Chromium with video
recording, tours the floor/feed, opens the newest Needs-You piece, clicks
Approve (a REAL Owner-Action write to the sheet), then saves the webm.

Usage: .venv/bin/python tools/record_console.py console.webm
"""
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "console.webm"
    server = subprocess.Popen(
        [str(ROOT / ".venv/bin/python"), str(ROOT / "tools/floor_serve.py")],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(2.5)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir=str(ROOT / "console_video"),
                record_video_size={"width": 1920, "height": 1080},
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8787", wait_until="networkidle")
            time.sleep(5)                              # the floor, breathing
            page.mouse.wheel(0, 500); time.sleep(3)    # feed
            page.mouse.wheel(0, 700); time.sleep(3)    # needs-you / ladder
            page.mouse.wheel(0, -1200); time.sleep(2)
            # open the newest Needs-You piece by its id (from the exported state)
            state = json.loads((ROOT / "ui/studio-floor/data/state.json").read_text())
            needs = [p for p in state.get("pieces", []) if p.get("needs_you")]
            target = needs[-1]["piece_id"] if needs else None
            print("target piece:", target)
            opened = False
            for sel in (f'.tray-item[data-piece="{target}"]',
                        f'.piece-chip[data-piece="{target}"]'):
                try:
                    page.locator(sel).first.click(timeout=3000)
                    opened = True
                    break
                except Exception:
                    continue
            if not opened and target:
                page.evaluate(f"openDrawer('{target}')")
            time.sleep(4.5)
            # click Approve in the drawer (real Owner-Action write)
            clicked = False
            try:
                page.locator("button.act-approve").first.click(timeout=5000)
                clicked = True
            except Exception:
                pass
            time.sleep(4 if clicked else 2)
            print("approve clicked:", clicked)
            video = page.video
            ctx.close()
            path = video.path()
            browser.close()
        pathlib.Path(out).unlink(missing_ok=True)
        pathlib.Path(path).rename(out)
        print("wrote", out)
    finally:
        server.terminate()


if __name__ == "__main__":
    main()
