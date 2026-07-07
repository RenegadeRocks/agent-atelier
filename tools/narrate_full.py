"""Narrate the assembled full-product demo (Gemini TTS, Charon voice).

Assembly order: partA1 (interview+cadence) → partF (the honest failure) →
partA2 (planned piece succeeds) → partB (console + Approve) → partC (poller
+ kit) → partE (artwork reveal). Anchors come from each cast's compressed
timeline; fixed times for video-only parts. Lines queue; never overlap.

Usage: .venv/bin/python tools/narrate_full.py full-silent.mp4 final.mp4
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

IDLE_LIMIT = 6.0
VOICE = "Charon"

A1 = [
    (r"the full promise", "This is Agent Atelier, live and unedited. The whole promise: give it your brand once, and a company of eight AI agents plans your weeks and makes your posts. Nothing publishes without a human."),
    (r"STEP 1", "It starts with an interview. A strategist agent reads the brand's documents — a chai and toast counter from Indore — and drafts everything it safely can."),
    (r"You: ", "Then it stops, and asks the owner for what it refuses to guess: what this brand must never claim, and never reveal. Safety comes from a human, on the record."),
    (r"Auto-retrying", "The compiled kit is validated by code, not by the model's word. The first attempt fails — so it is quarantined, never activated, and retried against the canonical template."),
    (r"now ACTIVE", "Validated. Active. This brand now exists — as pure configuration."),
    (r"STEP 2", "One command, and the scheduler composes the coming week for every brand in the studio. This is the cadence: three to six planned pieces per brand, every week, on rhythms the owner set."),
]
F = [
    (r"STEP 3", "Now, honestly: the first production run failed. The interview never captured a contact number, and the resolver refuses to run with an unresolved required field. It fails closed — never silent."),
    (r"ResolveBlocked|ERR_REQUIRED", "The owner adds one line of configuration. Later, the creative director blocked an entire draft over a non-disclosure rule, and that fix was one clarifying line too. Failures are part of a working system: caught, fixed, and logged in public."),
]
A2 = [
    (r"STEP 3", "The same planned slot, again. Watch carefully — no human provides an idea. The managing editor invents this week's concept itself, from the brand canon."),
    (r"\[research_verification\]", "A writer has drafted in the brand's voice; research verifies every claim against the safety rules from the interview."),
    (r"\[creative_director\]", "The creative director judges craft and compliance, and rejects with numbered, reproducible reasons."),
    (r"\[MCP image_generate\]", "The image is generated text-free, composited with the brand's own typography by code, then inspected — actual pixels — before sign-off."),
    (r"\[MCP sheets\]", "The finished piece lands in the approval queue: a Google Sheet. The system of record."),
    (r"STEP 4", "And everything the agents just did is exported to the owner's console."),
]
B = [
    (1.0, "This is the Studio Floor. Every agent, every handoff, and a trust ladder — autonomy here is earned, never assumed."),
    (12.0, "The piece the studio just made is waiting at the human gate."),
    (19.0, "One click: Approve. That click is a single write, to a single cell, in the sheet."),
]
C = [
    (r"STEP 6", "The poller sees the human's decision, re-runs the deterministic safety gauntlet — zero AI calls — and builds the deliverable."),
    (r"caption.txt", "A post kit: image, caption, alt text, checklist. Handed to a human to publish."),
]
E = [
    (0.8, "And this is the piece it made — for a brand that did not exist two hours ago. Brand in. Week planned. Piece made. Human gate held. Agent Atelier: the studio is constant; the brand is configuration."),
]

PARTS = [
    ("partA1.mp4", "partA1.cast", A1),
    ("partF.mp4", "partF.cast", F),
    ("partA2.mp4", "partA2.cast", A2),
    ("partB.mp4", None, B),
    ("partC.mp4", "partC.cast", C),
    ("partE.mp4", None, E),
]


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


def cast_events(cast_path):
    events = []
    with open(cast_path) as f:
        header = json.loads(f.readline())
        v3 = header.get("version") == 3
        prev, comp = 0.0, 0.0
        for line in f:
            t, kind, data = json.loads(line)
            if kind != "o":
                continue
            gap = t if v3 else (t - prev)
            comp += min(gap, IDLE_LIMIT)
            prev = t
            events.append((comp, data))
    return events


def tts(text, wav_path):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    resp = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE))),
        ),
    )
    pcm = resp.candidates[0].content.parts[0].inline_data.data
    raw = wav_path + ".pcm"
    open(raw, "wb").write(pcm)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar",
                    "24000", "-ac", "1", "-i", raw, "-ar", "48000", "-ac", "2",
                    wav_path], check=True)
    os.unlink(raw)


def main():
    silent, out = sys.argv[1], sys.argv[2]
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).resolve().parents[1] / ".env")

    anchors, offset = [], 0.0
    for video, cast, segments in PARTS:
        if cast:
            events = cast_events(cast)
            cursor = 0
            for pat, text in segments:
                rx = re.compile(pat)
                hit = next(((t, d) for t, d in events[cursor:] if rx.search(d)), None)
                if hit is None:
                    print(f"[narrate] missed in {cast}: {pat}")
                    continue
                cursor = next(i for i, e in enumerate(events) if e[0] >= hit[0])
                anchors.append((offset + hit[0], text))
        else:
            anchors += [(offset + t, text) for t, text in segments]
        offset += dur(video)
    anchors.sort(key=lambda x: x[0])

    tmp = pathlib.Path(tempfile.mkdtemp())
    inputs, filters, mixes = ["-i", silent], [], []
    prev_end = 0.0
    for i, (t, text) in enumerate(anchors):
        wav = str(tmp / f"n{i:02d}.wav")
        try:
            tts(text, wav)
        except Exception as e:
            print(f"[narrate] gemini tts failed ({e}); falling back to say")
            aiff = wav + ".aiff"
            subprocess.run(["say", "-v", "Samantha", "-r", "175", "-o", aiff, text], check=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", aiff,
                            "-ar", "48000", "-ac", "2", wav], check=True)
        d = dur(wav)
        start = max(t, prev_end + 0.6)
        prev_end = start + d
        print(f"[narrate] {start:7.1f}s ({d:4.1f}s)  {text[:64]}")
        inputs += ["-i", wav]
        ms = int(start * 1000)
        filters.append(f"[{i+1}:a]adelay={ms}|{ms}[a{i}]")
        mixes.append(f"[a{i}]")

    fc = ";".join(filters) + f";{''.join(mixes)}amix=inputs={len(mixes)}:normalize=0[aout]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out], check=True)
    print("[narrate] wrote", out, f"(video {dur(out):.0f}s, narration ends {prev_end:.0f}s)")


if __name__ == "__main__":
    main()
