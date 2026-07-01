#!/usr/bin/env python3
"""
build_view_split.py — derive build-view/ and specs/contracts/ from the PRD.

WHY THIS EXISTS
    The canonical PRD (specs/PRD-Agentic-Content-Studio.md, ~2,840 lines) is kept
    WHOLE — it is the reviewed source of truth. But building the whole thing from
    one 2,840-line file invites "context rot": as the input grows, the model's
    attention degrades and irrelevant sections act as distractors. So the BUILD is
    driven with *progressive disclosure*: for each phase the agent loads only a small
    always-on core + that contract's READ-SCOPE sections. This script produces those
    per-section views mechanically, so no human ever hand-splits the PRD.

WHAT IT PRODUCES  (all DERIVED — never hand-edit; regenerate after ANY PRD edit)
    build-view/
      sections/NN-slug.md            one file per top-level "## " section (+ appendices)
      core.md                        the always-load core: §0 + §3 + §5 + §17
      00-index.md                    the map: sections, source line ranges, and the
                                     per-contract READ-SCOPE -> file table (from §19.1)
      build-view.manifest.json       machine-readable section map
    specs/
      contracts/P0.md ... P6.md      the eleven §19.1 BUNNY contract blocks, carved out
    .agents/
      workflows/build-P0.md ...      one /command per contract (resume.md and
                                     change-request.md are hand-authored, NOT touched)

CORRECTNESS PROPERTIES
    * Fence-awareness (defense-in-depth). The PRD embeds YAML/code blocks whose lines
      begin with "#" (YAML comments), e.g. the Brand Kit block in §7 and the data-model
      block in §17. Section boundaries are cut only on LEVEL-2 "## " headings, and only
      OUTSIDE code fences — so neither a "# comment" nor a hypothetical "## " line inside
      a fence can create a bogus section. Today the level-2 filter alone keeps §7 whole
      (there are no "## " lines inside fences); the fence tracking is the belt to that
      suspenders, and applies equally to contract extraction.
    * Lossless. Preamble + all section bodies reconstruct the PRD byte-for-byte.

USAGE
    python3 tools/build_view_split.py            # REGENERATE all derived files (after a PRD edit)
    python3 tools/build_view_split.py --verify   # NON-MUTATING drift+invariant check (CI / after `git pull`)
                                                 #   exits 1 (writes nothing) if any derived file is
                                                 #   stale/missing/extra vs what the current PRD implies
    (--check is an alias of --verify, kept so older docs/hooks stay non-mutating.)

This file is authored source code (Day-4: instruction/rule files are source code).
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (repo root = parent of this tools/ dir)
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
PRD = REPO / "specs" / "PRD-Agentic-Content-Studio.md"
BUILD_VIEW = REPO / "build-view"
SECTIONS_DIR = BUILD_VIEW / "sections"
CONTRACTS_DIR = REPO / "specs" / "contracts"
WORKFLOWS_DIR = REPO / ".agents" / "workflows"

# Sections that make up the always-load core (by section id: "0".."21").
CORE_SECTION_IDS = ["0", "3", "5", "17"]

# The eleven contracts and their READ-SCOPE, transcribed verbatim from PRD §19.1.
# read_secs resolves to build-view section files; artifacts are non-PRD files.
CONTRACTS = [
    {"id": "P0", "phase": "0",
     "read_secs": ["18", "16", "app-d"], "artifacts": [],
     "read": "§18 (build workflow + governance), §16 (MCP contracts), Appendix D (file map)",
     "park": "§7–§15 — later phases"},
    {"id": "P1-A", "phase": "1",
     "read_secs": ["8", "9", "10"], "artifacts": [],
     "read": "§8 (roster + agent instruction files), §9.1–§9.4 (engine docs + linter), §10.1 (pipeline)",
     "park": "§7 (Brand Kit), §12.4, §14 — later phases"},
    {"id": "P1-B", "phase": "1",
     "read_secs": ["10", "11", "12", "16"], "artifacts": [],
     "read": "§10.1 (pipeline), §11.2 (Caption-Composer), §12.2 (Sheets integrity), §16.1 (MCP contracts)",
     "park": "§7, §12.4, §14 — later phases"},
    {"id": "P2-A", "phase": "2",
     "read_secs": ["7", "app-a"], "artifacts": [],
     "read": "§7.2 (Brand Kit schema), §7.2.1 (resolver), §7.3 (seeding map), Appendix A (worked kit)",
     "park": "§12.4, §14, §15 — later phases"},
    {"id": "P2-B", "phase": "2",
     "read_secs": ["7", "app-a"], "artifacts": [],
     "read": "§7.1 (intake + first-light), §7.8 (archetype starters), Appendix A",
     "park": "§12.4, §15.4 — later phases"},
    {"id": "P3", "phase": "3",
     "read_secs": ["7", "9", "13", "8"], "artifacts": [],
     "read": "§7.4 (Offerings), §9.4 (ledger-linter), §9.5 + §13 (cadence + control loop), §8.2",
     "park": "§12.4, §14.2 — later phases"},
    {"id": "P4-A", "phase": "4",
     "read_secs": ["14", "13", "15", "18", "10"], "artifacts": ["specs/policies.yaml"],
     "read": "§14.2 (Policy Server + claim-grounding + fail-closed), §13.2 (circuit-breaker), "
             "§15.1–§15.3 + §18.2 (CI eval gate + golden set), §10.3 (blocker scenarios), policies.yaml",
     "park": "§12.4 and the publish-time referee (P4-B)"},
    {"id": "P4-B", "phase": "4",
     "read_secs": ["14", "15"], "artifacts": [],
     "read": "§14.2 (publish-time semantic referee), §14.7 (untrusted content), §15.4 (adversarial suite)",
     "park": "the UI (P5)"},
    {"id": "P5-A", "phase": "5",
     "read_secs": ["12"], "artifacts": [],
     "read": "§12.1 (Review app), §12.3 (publishing + Post Kit + mark-as-posted), "
             "§12.5 (approval protocol), §12.2 (Sheets integrity)",
     "park": "§12.4 (Studio Floor → P5-B)"},
    {"id": "P5-B", "phase": "5",
     "read_secs": ["12", "5", "8", "14"], "artifacts": [],
     "read": "§12.4 (Studio Floor — the whole section), §5.3/§8.3 (progressive disclosure), "
             "§14.5 (observability spans)",
     "park": "P6 material"},
    {"id": "P6", "phase": "6",
     "read_secs": ["15", "12", "7"], "artifacts": [],
     "read": "§15.3 (post-publication audit + golden set), §12.2 (scaling/migration), §7.8 (multi-brand)",
     "park": "Final phase — nothing to park"},
]

EXPECTED_CONTRACT_IDS = ["P0", "P1-A", "P1-B", "P2-A", "P2-B", "P3",
                         "P4-A", "P4-B", "P5-A", "P5-B", "P6"]
FIELD_ANCHORS = ["INTENT", "SCOPE", "NON-GOALS", "INPUTS", "INVARIANTS",
                 "ACTION", "ACCEPTANCE", "VERIFY", "AUTHORIZATION", "ON-FAIL"]

FENCE_RE = re.compile(r"^\s*(```|~~~)")
H_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
NUM_RE = re.compile(r"^(\d+)\.\s+(.*)$")
APP_RE = re.compile(r"^Appendix\s+([A-Za-z])\b\s*[—–-]?\s*(.*)$")
CONTRACT_RE = re.compile(r"^\*\*CONTRACT\s+(\S+)\s")
GATE_RE = re.compile(r"^→\s*\*\*GATE")

DERIVED = ("<!-- DERIVED build-view file — do NOT hand-edit. Regenerate with "
           "`python3 tools/build_view_split.py`. Source of truth: "
           "specs/PRD-Agentic-Content-Studio.md -->\n\n")


def slugify(text: str, maxlen: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    s = re.sub(r"-+", "-", s).strip("-")
    if len(s) > maxlen:
        cut = s[:maxlen].rsplit("-", 1)[0]
        s = cut or s[:maxlen]
    return s


def code_mask(lines: list[str]) -> list[bool]:
    """True where a line is a fence marker or inside a fenced code block."""
    mask = [False] * len(lines)
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            mask[i] = True
            in_fence = not in_fence
        else:
            mask[i] = in_fence
    return mask


def parse_heading(title: str):
    """Return (section_id, filename_key) for a level-2 heading's text."""
    m = NUM_RE.match(title)
    if m:
        num = int(m.group(1))
        return str(num), f"{num:02d}-{slugify(m.group(2))}"
    m = APP_RE.match(title)
    if m:
        letter = m.group(1).lower()
        rest = slugify(m.group(2))
        key = f"app-{letter}-{rest}" if rest else f"app-{letter}"
        return f"app-{letter}", key
    return slugify(title), slugify(title)


def split_sections(lines: list[str]):
    """Fence-aware split into (preamble, sections). Each section is a dict."""
    mask = code_mask(lines)
    boundaries = []  # (line_index, section_id, filename_key, title)
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        m = H_RE.match(line)
        if m and len(m.group(1)) == 2:  # top-level "## " heading only, outside fences
            sid, key = parse_heading(m.group(2))
            boundaries.append((i, sid, key, m.group(2)))
    if not boundaries:
        raise SystemExit("ERROR: no '## ' sections found — is the PRD intact?")

    preamble = "".join(lines[: boundaries[0][0]])
    sections = []
    for idx, (start, sid, key, title) in enumerate(boundaries):
        end = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        sections.append({
            "id": sid, "key": key, "title": title,
            "filename": f"{key}.md",
            "start_line": start + 1,       # 1-based, inclusive
            "end_line": end,              # 1-based, inclusive
            "body": "".join(lines[start:end]),
        })
    seen = {}
    for s in sections:
        if s["filename"] in seen:
            raise SystemExit(f"ERROR: duplicate section filename {s['filename']!r} "
                             f"(§{seen[s['filename']]} and §{s['id']})")
        seen[s["filename"]] = s["id"]
    return preamble, sections


def extract_contracts(text: str):
    """Carve the eleven §19.1 CONTRACT blocks (CONTRACT header .. its GATE line).

    Fence-aware: CONTRACT / GATE markers inside a code fence are ignored, so a fenced
    example of the contract template can never truncate a real contract at a fake gate.
    """
    lines = text.splitlines(keepends=True)
    mask = code_mask(lines)
    starts = [i for i, ln in enumerate(lines) if not mask[i] and CONTRACT_RE.match(ln)]
    blocks = []
    for s in starts:
        cid = CONTRACT_RE.match(lines[s]).group(1)
        gate = next((j for j in range(s, len(lines))
                     if not mask[j] and GATE_RE.match(lines[j])), None)
        if gate is None:
            raise SystemExit(f"ERROR: contract {cid} has no closing '→ **GATE' line")
        blocks.append((cid, "".join(lines[s:gate + 1])))
    return blocks


def gate_line(block: str) -> str:
    for ln in block.splitlines():
        if GATE_RE.match(ln):
            return ln.strip().lstrip("→").strip()
    return ""


def resolve_files(read_secs, by_id):
    out = []
    for sid in read_secs:
        s = by_id.get(sid)
        if not s:
            raise SystemExit(f"ERROR: READ-SCOPE references §{sid} but no such section")
        out.append(s["filename"])
    return out


# ---------------------------------------------------------------------------
# Renderers — pure: build {Path: content}. No I/O here.
# ---------------------------------------------------------------------------
def render_sections(sections):
    out = {}
    for s in sections:
        banner = (f"<!-- DERIVED from specs/PRD-Agentic-Content-Studio.md §{s['id']} "
                  f"(source lines {s['start_line']}–{s['end_line']}). Do NOT hand-edit; "
                  f"regenerate with tools/build_view_split.py after PRD edits. -->\n\n")
        out[SECTIONS_DIR / s["filename"]] = banner + s["body"]
    return out


def render_core(preamble, sections):
    by_id = {s["id"]: s for s in sections}

    def trimmed(body: str) -> str:
        b = body.rstrip()
        if b.endswith("---"):
            b = b[:-3].rstrip()
        return b

    parts = [DERIVED,
             "# build-view/core.md — the always-load build core\n\n",
             "> Load THIS file for **every** contract, alongside `GEMINI.md`/`AGENTS.md` "
             "(which Antigravity always loads) and the contract's own READ-SCOPE files. "
             "It is the shared vocabulary — orientation, the goals/metrics bar, the "
             "conceptual model, and the data-model / `piece_id` spine. Nothing else is "
             "global; everything else loads per contract.\n\n"
             f"> Core = §{', §'.join(CORE_SECTION_IDS)}. Each also exists individually in "
             "`build-view/sections/`.\n\n---\n\n",
             "## PRD preamble\n\n", trimmed(preamble), "\n\n---\n\n"]
    for sid in CORE_SECTION_IDS:
        if sid not in by_id:
            raise SystemExit(f"ERROR: core section §{sid} not found")
        parts.append(trimmed(by_id[sid]["body"]) + "\n\n---\n\n")
    return {BUILD_VIEW / "core.md": "".join(parts)}


def render_index(preamble, sections):
    by_id = {s["id"]: s for s in sections}
    used_by = {s["id"]: [] for s in sections}
    for c in CONTRACTS:
        for sid in c["read_secs"]:
            if sid in used_by:
                used_by[sid].append(c["id"])
    core_set = set(CORE_SECTION_IDS)

    L = [DERIVED, "# build-view/00-index.md — the build navigation map\n\n",
         "The PRD is kept whole at `specs/PRD-Agentic-Content-Studio.md`. This folder is a "
         "**derived, read-only view** for building without context rot: load "
         "`build-view/core.md` + your contract's READ-SCOPE files only — never the whole PRD.\n\n",
         "## Sections\n\n",
         "| § | File | Source lines | In core? | Read by contracts |\n",
         "|---|------|-------------|----------|-------------------|\n"]
    for s in sections:
        core = "✅ core" if s["id"] in core_set else ""
        ub = ", ".join(used_by[s["id"]]) or "—"
        disp = f"§{s['id']}" if s["id"].isdigit() else f"App {s['id'].split('-')[-1].upper()}"
        L.append(f"| {disp} | `sections/{s['filename']}` | {s['start_line']}–{s['end_line']} "
                 f"| {core} | {ub} |\n")

    L.append("\n## Per-contract READ-SCOPE → files (from PRD §19.1)\n\n"
             "For each contract, load **`core.md` + these files** (plus `GEMINI.md`/`AGENTS.md`, "
             "always loaded). Everything else is parked. The `.agents/workflows/build-<id>.md` "
             "command for each contract lists the same set.\n\n"
             "| Contract | READ-SCOPE (PRD text) | Load these build-view files | Park |\n"
             "|----------|-----------------------|-----------------------------|------|\n")
    for c in CONTRACTS:
        files = resolve_files(c["read_secs"], by_id)
        files_disp = "<br>".join(["`core.md`"] + [f"`sections/{f}`" for f in files]
                                 + [f"`{a}`" for a in c["artifacts"]])
        L.append(f"| **{c['id']}** | {c['read']} | {files_disp} | {c['park']} |\n")

    L.append("\n## Contracts (BUNNY) \n\nThe eleven gated prompt-contracts are carved from §19.1 "
             "into `specs/contracts/P*.md` (also derived — regenerate the splitter after §19 edits). "
             "The full roadmap is §19 (`sections/" + by_id["19"]["filename"] + "`).\n")
    return {BUILD_VIEW / "00-index.md": "".join(L)}


def render_manifest(sections):
    by_id = {s["id"]: s for s in sections}
    manifest = {
        "source": "specs/PRD-Agentic-Content-Studio.md",
        "generated_by": "tools/build_view_split.py",
        "core_section_ids": CORE_SECTION_IDS,
        "sections": [{"id": s["id"], "title": s["title"].strip(),
                      "file": f"build-view/sections/{s['filename']}",
                      "start_line": s["start_line"], "end_line": s["end_line"],
                      "in_core": s["id"] in CORE_SECTION_IDS} for s in sections],
        "contracts": [{"id": c["id"], "phase": c["phase"],
                       "contract_file": f"specs/contracts/{c['id']}.md",
                       "workflow": f".agents/workflows/build-{c['id']}.md",
                       "read_scope_text": c["read"],
                       "load_files": ["build-view/core.md"]
                       + [f"build-view/sections/{by_id[s]['filename']}" for s in c["read_secs"]]
                       + c["artifacts"],
                       "park": c["park"]} for c in CONTRACTS],
    }
    return {BUILD_VIEW / "build-view.manifest.json":
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"}


def render_contracts(blocks):
    out = {}
    for cid, body in blocks:
        banner = (f"<!-- DERIVED from PRD §19.1 (CONTRACT {cid}). Do NOT hand-edit; regenerate "
                  f"with tools/build_view_split.py after §19 edits. The PRD is the source of truth; "
                  f"this contract governs the build, it does not replace the spec. -->\n\n")
        out[CONTRACTS_DIR / f"{cid}.md"] = banner + body.rstrip() + "\n"
    return out


def render_workflows(sections, blocks):
    by_id = {s["id"]: s for s in sections}
    gates = {cid: gate_line(body) for cid, body in blocks}
    ids = [c["id"] for c in CONTRACTS]
    out = {}
    for i, c in enumerate(CONTRACTS):
        cid = c["id"]
        nxt = ids[i + 1] if i + 1 < len(ids) else None
        files = resolve_files(c["read_secs"], by_id)
        load_lines = ["- `build-view/core.md`  — the always-load core (load every time)"]
        for sid, fn in zip(c["read_secs"], files):
            disp = f"§{sid}" if sid.isdigit() else f"Appendix {sid.split('-')[-1].upper()}"
            load_lines.append(f"- `build-view/sections/{fn}`  — {disp}")
        for a in c["artifacts"]:
            load_lines.append(f"- `{a}`  — authored artifact")
        publish_note = ("" if cid in ("P0", "P1-A") else
                        "- **Mandatory before any publish path:** the ledger-linter test "
                        "(a rotation-violating draft is rejected pre-CD) and the fail-closed "
                        "safety test must exist and pass.\n")
        p0_note = ("- **Naming:** the proposed product source tree must NOT use directory names "
                   "the repo `.gitignore` excludes (`build/`, `dist/`, `node_modules/`) or that "
                   "source would be silently untracked and lost on `git pull`. Prefer a named "
                   "package dir (e.g. `app/`) and scope any build/dist ignores under it.\n"
                   if cid == "P0" else "")
        nxt_line = (f"On owner AUTHORIZATION, run `.agents/workflows/build-{nxt}.md`."
                    if nxt else "This is the final contract. On its gate, the system is "
                    "**feature-complete vs the PRD** (§19.3, §21).")

        body = f"""<!-- DERIVED — regenerate with `python3 tools/build_view_split.py`. Do NOT hand-edit.
The ten-field contract is specs/contracts/{cid}.md; the PRD (§19.1) is the source of truth. -->

# /build-{cid} — Contract {cid} (Phase {c['phase']})

Run this for **one** contract only, in a fresh context. Obey `.agents/rules/build-protocol.md`
and `GEMINI.md`. If you are picking up a half-finished {cid}, run
`.agents/workflows/resume.md` first.

**Prereq:** the previous contract is verified, committed, and the owner authorized {cid}
(check `BUILD-STATUS.md`).

## STEP 1 — Load ONLY these (context-rot discipline)
Read only the following. **Do NOT open the whole PRD.** `GEMINI.md` / `AGENTS.md` are
already always-loaded by the tool.
{chr(10).join(load_lines)}
- `specs/contracts/{cid}.md`  — the ten-field BUNNY contract for this unit

**Parked for later (do not read now):** {c['park']}.

## STEP 2 — Honor the contract
`specs/contracts/{cid}.md` is the contract. Its READ-SCOPE (verbatim from §19.1):
> read {c['read']}.

Follow INTENT · SCOPE · NON-GOALS · INPUTS · INVARIANTS · ACTION exactly. **NON-GOALS are
hard boundaries** — do not build a later phase's work "while you're here."

## STEP 3 — Test-first → build → verify (build-protocol §1)
- Propose the files/structure first; wait for owner OK (no-YOLO).
{p0_note}- Author the contract's ACCEPTANCE/VERIFY behaviour as a **failing** Gherkin suite first
  (red), then implement to green. Add it to the growing regression suite.
{publish_note}- Build component-by-component to SCOPE/ACTION; show diffs; verify model IDs / deps
  against live docs (GEMINI.md §4).
- **VERIFY with captured evidence** (report-is-not-the-repo): run the piece / fire the negative test / capture the run.

## STEP 4 — Gate
GATE = the phase's test suite green **AND** the CI eval gate passes (build-protocol §1.6).
Contract gate (from §19.1):
> {gates.get(cid, '(see specs/contracts/' + cid + '.md)')}

## STEP 5 — Record & hand off (before you stop)
- Commit when the owner asks: `{cid}: <what landed> — <gate state>`.
- Update `BUILD-STATUS.md` — tick {cid}{"; next = " + nxt if nxt else " (final)"}.
- Update `WORKLOG.md` (contract, done, remaining, **next action**) — always, even if continuing.
- Log any deviation in `specs/deviation_log.md` (assumption → ground truth → decision).
- Get owner **AUTHORIZATION** to release the next contract (you do not self-authorize).

## Next
{nxt_line}
"""
        out[WORKFLOWS_DIR / f"build-{cid}.md"] = body
    return out


def render_all(preamble, sections, blocks):
    out = {}
    out.update(render_sections(sections))
    out.update(render_core(preamble, sections))
    out.update(render_index(preamble, sections))
    out.update(render_manifest(sections))
    out.update(render_contracts(blocks))
    out.update(render_workflows(sections, blocks))
    return out


# The glob patterns that identify DERIVED files we own (for clean + stale detection).
DERIVED_GLOBS = [(SECTIONS_DIR, "*.md"), (CONTRACTS_DIR, "P*.md"), (WORKFLOWS_DIR, "build-P*.md")]


def emit(rendered):
    for d, pat in DERIVED_GLOBS:
        if d.exists():
            for f in d.glob(pat):
                f.unlink()
    for path, content in rendered.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def verify(rendered) -> list[str]:
    """Compare on-disk derived files to what the current PRD implies. No writes."""
    problems = []
    for path, content in rendered.items():
        if not path.exists():
            problems.append(f"MISSING derived file: {path.relative_to(REPO)}")
        elif path.read_text(encoding="utf-8") != content:
            problems.append(f"STALE derived file (differs from PRD): {path.relative_to(REPO)}")
    rendered_set = set(rendered)
    for d, pat in DERIVED_GLOBS:
        if d.exists():
            for f in d.glob(pat):
                if f not in rendered_set:
                    problems.append(f"EXTRA derived file (no longer generated): {f.relative_to(REPO)}")
    return problems


def assert_invariants(sections, blocks) -> list[str]:
    problems = []
    ids = {s["id"] for s in sections}
    got_ids = [cid for cid, _ in blocks]
    # 1. §7 stays whole (fence/level-2 regression canary).
    s7 = next((s for s in sections if s["id"] == "7"), None)
    if not s7 or (s7["end_line"] - s7["start_line"]) < 400:
        problems.append("§7 looks shattered — fence/level-2 split failed (Brand Kit YAML).")
    # 2. Contract set matches expectation exactly.
    if got_ids != EXPECTED_CONTRACT_IDS:
        problems.append(f"contract ids {got_ids} != expected {EXPECTED_CONTRACT_IDS}")
    # 3. Core sections present.
    for c in CORE_SECTION_IDS:
        if c not in ids:
            problems.append(f"core section §{c} missing")
    # 4. Every contract READ-SCOPE resolves.
    for c in CONTRACTS:
        for sid in c["read_secs"]:
            if sid not in ids:
                problems.append(f"{c['id']} READ-SCOPE §{sid} unresolved")
    # 5. Each carved contract has all 10 field anchors + a gate (guards fence-truncation).
    for cid, body in blocks:
        for anchor in FIELD_ANCHORS:
            if f"**{anchor}**" not in body:
                problems.append(f"{cid} contract missing field **{anchor}** (truncated?)")
        if not gate_line(body):
            problems.append(f"{cid} has no gate line")
    return problems


def main():
    args = sys.argv[1:]
    verify_only = ("--verify" in args) or ("--check" in args)
    if not PRD.exists():
        raise SystemExit(f"ERROR: PRD not found at {PRD}")
    text = PRD.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    preamble, sections = split_sections(lines)
    blocks = extract_contracts(text)
    rendered = render_all(preamble, sections, blocks)

    inv = assert_invariants(sections, blocks)

    if verify_only:
        drift = verify(rendered)
        problems = inv + drift
        if problems:
            print("VERIFY FAILED — the derived files are out of sync with the PRD "
                  "(or the PRD parse is broken):")
            for p in problems:
                print("  -", p)
            print("\nFix: run `python3 tools/build_view_split.py` to regenerate, then commit "
                  "the PRD edit + the regenerated derived files together.")
            raise SystemExit(1)
        print(f"VERIFY PASSED: {len(sections)} sections, 11 contracts, core complete, all "
              f"READ-SCOPE refs resolve, and every derived file matches the current PRD.")
        return

    emit(rendered)
    if inv:
        print("REGENERATED, but invariants failed:")
        for p in inv:
            print("  -", p)
        raise SystemExit(1)
    print(f"build-view: {len(sections)} sections → {SECTIONS_DIR}")
    print(f"core.md: §{', §'.join(CORE_SECTION_IDS)}")
    print(f"contracts: {len(blocks)} → {CONTRACTS_DIR}  ({', '.join(cid for cid, _ in blocks)})")
    print(f"workflows: {len(CONTRACTS)} build-*.md → {WORKFLOWS_DIR}")
    print("OK. To check the tree stays in sync later: python3 tools/build_view_split.py --verify")


if __name__ == "__main__":
    main()
