# /change-request — change the spec mid-build (without a full-context session)

Use this when, **while building**, you find something in the spec is wrong or needs to
change — e.g. an agent prompt in `specs/agents/…` produces bad output, a policy is too
strict, a canon doc is off. The rule (GEMINI.md §3.7): **the spec is durable, code is
disposable — fix the spec artifact, not just the code.** You do NOT need the original
authoring session's full context; the deviation log carries the intent forward.

## A. Small change (a prompt, a policy line, a canon tweak)

1. **Edit it where it lives.** The running system reads these files directly:
   - agent behaviour → `specs/agents/<agent>.md`
   - engine/canon → `specs/canon/…`
   - permissions → `specs/policies.yaml`
   - a brand fact → `brands/<brand>/brand_kit.yaml` (never hardcode; it's config)
   - schema/resolver → `specs/brand_kit.schema.json` / `specs/resolver.md`
2. **Log it** in `specs/deviation_log.md` (append an entry):
   `assumption → ground truth / reason → decision → files touched → date`.
   This is the audit surface (§14.5) and the context a later session needs.
3. **Re-run the affected tests.** If behaviour changed, update the Gherkin first (red),
   then make it green. Keep the regression suite green.
4. **If the change is high-stakes** (enabling auto-publish, a schema/canon change): it
   needs an owner **Vibe-Diff** + authorization before it lands (§14.4).

## B. The change touches the PRD itself

The PRD is the source of truth; `build-view/` is derived from it.

1. Edit the owning **PRD section** in `specs/PRD-Agentic-Content-Studio.md`.
2. **Re-run the splitter** so build-view + contracts + workflows regenerate from the new
   text — never hand-edit build-view/, specs/contracts/, or `.agents/workflows/build-*.md`:
   ```
   python3 tools/build_view_split.py            # regenerate the derived view
   python3 tools/build_view_split.py --verify   # confirm the tree now matches the PRD (writes nothing)
   ```
3. Log the change in `specs/deviation_log.md` and, if a phase's READ-SCOPE changed,
   sanity-check the regenerated `build-view/00-index.md` table.

## C. Large redesign (not a tweak)

Treat it as a spec revision, not an inline patch:
1. Author the revision focused on the affected section(s); keep the BUNNY contracts
   coherent with it.
2. Re-verify (the same adversarial red-team discipline the PRD was built under).
3. Re-run the splitter (step B.2).
4. Resume the build from where you were (`resume.md`).

## D. Commit the change atomically (so the other PC pulls a consistent tree)

After A / B / C, **commit and push in one commit**: the edited artifact(s) **and** the PRD
edit **and** the regenerated `build-view/` + `specs/contracts/` + `.agents/workflows/build-*.md`
**and** the `specs/deviation_log.md` entry — together (build-protocol §2/§3). Never commit a
PRD edit without its regenerated derived files, or the other PC will build against a stale
spec. A CI / pre-commit step running `python3 tools/build_view_split.py --verify` catches
that mistake.

## Why this works without full context

The **deviation log** is the memory. Any later session — or the other PC — can reconcile
correctly with only {the deviation entry + the one affected section + the consistency
rules in GEMINI.md}. It does not need the session that first authored the spec.
Human-in-the-loop gates are *where* you catch bad output — that is the system working,
not failing.
