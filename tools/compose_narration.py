"""Overlay a TTS voiceover onto an agg-rendered demo recording.

Reads the .cast file, computes the COMPRESSED timeline (matching agg's
--idle-time-limit and --speed), anchors each narration line to the first
terminal event matching its pattern, generates TTS per line (macOS `say`),
and muxes everything over the silent mp4.

Usage: python tools/compose_narration.py demo.cast demo.mp4 demo-narrated.mp4
"""
import json
import re
import subprocess
import sys
import tempfile
import pathlib

IDLE_LIMIT = 6.0   # must match record_demo.sh (agg --idle-time-limit)
SPEED = 1.0        # must match agg --speed if used

SEGMENTS = [
    (r"a live, unedited run", "This is Agent Atelier, running live. One command, one idea for a Jaipur ice pop brand, and a company of eight AI agents takes it from here."),
    (r"\[managing_editor\]", "The managing editor plans the piece and delegates it down the studio."),
    (r"\[evergreen_content\]", "A writer drafts the caption and the visual brief, in the brand's own voice."),
    (r"\[research_verification\]", "Research verifies every claim against the brand's own safety rules, nothing is guessed."),
    (r"\[creative_director\] ", "Now the creative director judges the work. Craft first, compliance always. It rejects weak drafts with numbered, reproducible reasons."),
    (r"\[MCP image_generate\]", "Approved. The image is generated completely text free, then composited with the brand's real typography, by code."),
    (r"creative_director - Render Pass", "And the director inspects the actual pixels before signing off. It does not approve blind."),
    (r"\[MCP sheets\]", "The finished piece lands in a Google Sheet. The system of record. Nothing publishes from here on its own."),
    (r"SCENE 2", "This exports the studio floor. The console view of everything you just watched."),
    (r"SCENE 3", "Now the human gate. I approve the piece. One write, to one cell, in that sheet."),
    (r"SCENE 4", "The poller sees the human's decision, re-runs the full deterministic safety gauntlet, and only then builds the deliverable."),
    (r"SCENE 5", "The post kit. The image, the caption, alt text, and a posting checklist. Handed to a human to publish."),
    (r"DONE", "Eight agents did the work. A human held the last gate. That is Agent Atelier."),
]


def compressed_timeline(cast_path):
    """Yield (compressed_time, text) per event, applying the idle cap."""
    events = []
    with open(cast_path) as f:
        header = json.loads(f.readline())
        v3 = header.get("version") == 3  # v3 stores per-event DELTAS, v2 absolute times
        raw_prev, comp = 0.0, 0.0
        for line in f:
            t, kind, data = json.loads(line)
            if kind != "o":
                continue
            gap = t if v3 else (t - raw_prev)
            comp += min(gap, IDLE_LIMIT)
            raw_prev = t
            events.append((comp / SPEED, data))
    return events


def main():
    cast, video, out = sys.argv[1], sys.argv[2], sys.argv[3]
    events = compressed_timeline(cast)

    anchors = []
    cursor = 0
    for pat, text in SEGMENTS:
        rx = re.compile(pat)
        hit = next(((t, d) for t, d in events[cursor:] if rx.search(d)), None)
        if hit is None:
            print(f"[narrate] pattern not found, skipping: {pat}")
            continue
        t = hit[0]
        cursor = next(i for i, e in enumerate(events) if e[0] >= t)
        anchors.append((t, text))
        print(f"[narrate] {t:7.1f}s  {text[:60]}")

    tmp = pathlib.Path(tempfile.mkdtemp())
    inputs, filters, mixes = ["-i", video], [], []
    prev_end = 0.0  # never let two lines overlap: queue behind the previous one
    for i, (t, text) in enumerate(anchors):
        aiff = tmp / f"n{i:02d}.aiff"
        subprocess.run(["say", "-v", "Samantha", "-r", "175", "-o", str(aiff), text], check=True)
        wav = tmp / f"n{i:02d}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff),
                        "-ar", "48000", "-ac", "2", str(wav)], check=True)
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(wav)], capture_output=True, text=True).stdout.strip())
        start = max(t, prev_end + 0.5)
        prev_end = start + dur
        inputs += ["-i", str(wav)]
        delay_ms = int(start * 1000)
        filters.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms}[a{i}]")
        mixes.append(f"[a{i}]")

    if not mixes:
        sys.exit("[narrate] no anchors matched — nothing to compose")
    fc = ";".join(filters) + f";{''.join(mixes)}amix=inputs={len(mixes)}:normalize=0[aout]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out], check=True)
    print(f"[narrate] wrote {out}")


if __name__ == "__main__":
    main()
