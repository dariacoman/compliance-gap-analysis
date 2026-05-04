# Build Readiness

> Items to complete before starting ING-01. When everything in this doc is checked, you and your assistant can begin the build cleanly — no setup detours, no fuzzy decisions, no half-known corpus.
>
> Order roughly matches dependency. Each item has an **acceptance** line — that's what "done" looks like.

---

## 1. Set up the local environment

**Action:** Create the virtual environment, install dependencies, copy the env file template.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and paste your Groq API key after `GROQ_API_KEY=`. (Get one free at console.groq.com if you don't have it yet.)

**Acceptance:** `python -c "import sentence_transformers, torch, spacy, streamlit, groq, pypdf"` runs with no errors.

**Why this first:** Nothing else works without it. Catching dependency or Python-version issues now is cheap; catching them mid-ING-01 is expensive.

---

## 2. Verify the empty src/ skeleton runs

**Action:** Confirm the scaffolding files committed in this PR are in place and importable.

```bash
ls src/
ls src/llm/
ls tests/
pytest tests/  # should report "no tests collected" or 0 passed, no errors
```

**Acceptance:** Every file listed in `docs/build-notes.md` § "Repo layout" exists. `pytest` runs without import errors.

**Why:** The scaffolding gives every CAP-ID a home. Your assistant doesn't need to negotiate where things go — the slot is already named.

---

## 3. Run the corpus validation script

**Action:** Run the script that checks the corpus against the v2 corpus spec § 8 criteria.

```bash
python scripts/validate_corpus.py
```

The script (committed in this PR) checks: every file present per layout, every text file non-empty and at least 90% of expected word count, every `manifest.json` entry contains required fields, SHA-256 hashes regenerable and matching.

**Acceptance:** Script reports all checks green. If a check fails, see § 4 below.

**Why:** Catches corpus drift (a file that didn't extract correctly, a hash mismatch from an accidental edit) *before* it becomes a mid-build mystery.

---

## 4. Verify the corpus quality fixes from this PR

This PR includes two corpus fixes found during the pre-build review. Step 3 (`validate_corpus.py`) catches any issue if a fix didn't land cleanly; this section is your sign-off on the changes themselves.

### 4a. Filename and directory normalisation — fixed in this PR

The deployer-extras corner of the filesystem was inconsistent with every other corpus subdirectory: directory was `deployer extras/` (with a space) containing underscored filenames (`novara_talentlens_dpia.md`), while everything else used hyphenated no-space names. More importantly, the manifest's recorded paths followed the canonical convention — meaning the manifest pointed to files that didn't exist on disk. Validation would have failed before the build started.

**What changed:**

- Directory renamed: `corpus/deployer extras/` → `corpus/deployer-extras/`
- 5 files renamed underscore → hyphen to match the manifest's recorded paths exactly
- SHA-256 hashes are content-based; renaming preserved them, so no manifest regeneration was needed
- `v2_corpus_specification.md` § 2 updated: governance report filename loses "annual"; intake assessment filename word order matches manifest; operational subtree fully shown (including `ico-genai-consultation/` and `ico-audit-framework/` which were optional extensions per § 3.2 and got included)
- `v2_corpus_specification.md` § 4 file-count column updated (24 → 36 files; word-count ranges still valid)

**Acceptance:** Step 3's `validate_corpus.py` reports green. Spot-check one renamed file (e.g., `corpus/deployer-extras/novara-talentlens-dpia.md`) and confirm it opens with the expected content.

### 4b. Audit-framework overview stub — fixed in this PR

The original `corpus/operational/ico-audit-framework/01-overview.txt` was 62 words / 360 bytes, almost certainly a failed fetch. Re-fetched from the ICO source URL; the manifest entry was updated with new word-count and SHA-256.

**Acceptance:** Open `corpus/operational/ico-audit-framework/01-overview.txt`. Content reads as substantive guidance, not navigation cruft. Word count is materially larger than 62.

---

## 5. Read the AI Act extraction notes and confirm

**Action:** Open `docs/ai-act-extraction-notes.md`, read the observations on the EU AI Act `.txt` extraction quality, and decide whether the proposed article-boundary detection approach is workable.

**Acceptance:** You've read the notes. The approach is either confirmed or you've added a note explaining why a different approach is needed — but no code is written yet.

**Why:** ING-02's whole chunking design depends on what those 93,565 words actually look like — page furniture, column breaks, footnote spillage. Sketching the approach now is much cheaper than discovering issues mid-build.

---

## 6. Read the Novara policy and extras yourself

**Action:** Open and read at least once, not skim:

- `corpus/deployer/novara-ai-policy-v3.1.txt` (~15 pages)
- `corpus/deployer-extras/novara-talentlens-dpia.md`
- `corpus/deployer-extras/novara-talentlens-model-card.md`
- `corpus/deployer-extras/novara-talentlens-transparency-notice.md`
- `corpus/deployer-extras/novara-2025-ai-governance-report.md`
- `corpus/deployer-extras/novara-talentlens-model-intake-assessment.md`

Take rough notes on what each document covers and — more importantly — what it *doesn't* cover. The intentional gaps in these extras are the silence cases the system is designed to surface.

**Acceptance:** You can list, in your own words, three obligations the regulation places on a deployer that the Novara policy genuinely doesn't address.

**Why:** Your test queries (next item) need to target real silence cases, not imagined ones. You also need to be able to defend in viva *why* a particular silence finding is meaningful — that requires you knowing the policy as well as the regulation.

---

## 7. Confirm or override the decisions doc

**Action:** Read `docs/decisions.md` end to end. For each numbered decision (1–10), decide: accept as recommended, or override.

If you override, replace the **Decided** value with your call and add a short reason. Don't delete the alternative — markers reward the trade-off discussion either way.

**Acceptance:** Every decision has either an unmodified pre-build recommendation or a documented override. No question marks left.

**Why:** These are the values your code will use. Last cheap moment to push back on any of them is now.

---

## 8. Sketch your build-phase availability

**Action:** For Decision #10 in `docs/decisions.md` (build-phase budget commitment), sketch your availability against the build phase. You don't need a calendar — just an honest estimate:

- Roughly how many focused hours per week you expect, on average
- Any weeks where availability drops materially (exam periods, deadlines from other modules, family commitments)
- Whether the spec's 12–15 hr/week assumption is realistic for you

Add the sketch as a one-paragraph note under Decision #10 in `docs/decisions.md`.

**Acceptance:** Decision #10 has your honest estimate written down. If any stretch is materially below assumed budget, FLEX-5 invocation is flagged as a candidate for that stretch.

**Why:** This is the one decision only you can make. It also gives you a defendable narrative in the report's limitations section if the build runs hot ("the build was sized assuming X hours/week; actual was Y; here's how I adapted").

---

## 9. Draft the 5 hand-written test queries

**Action:** Open `docs/test-queries.md` (committed in this PR with 5 draft examples). Read the drafts. Replace each with a query in your own voice, or confirm the draft.

The 5 queries should span:

1. **Multi-facet** — forces the decompose step to actually decompose (≥3 sub-questions)
2. **Single, strong-match expected** — verifies the chain finds and cites adequate policy evidence
3. **Single, likely partial** — tests how the system handles policies that *touch* the obligation but don't fully address it
4. **Ambiguous** — tests how the system handles a query with unclear regulatory framing
5. **Deliberate silence target** — pick an obligation you confirmed (in step 6) the Novara policy doesn't address; verifies silence detection fires

**Acceptance:** 5 queries written, each tagged with which shape it targets. Each query is something Maya (Head of AI Compliance) plausibly types into the demo.

**Why:** These are the only build-time evaluation surface. They gate the retrieval-config freeze, the build-completion stage 1, and the demo. Quality matters more than quantity — 5 well-chosen queries are far more diagnostic than 20 random ones.

---

## 10. Hook your local `CLAUDE.md` into the committed docs

**Action:** Your personal `CLAUDE.md` (gitignored) should import the committed scaffolding so your assistant has full context every session.

Suggested top of your `CLAUDE.md`:

```markdown
# Personal Claude Code instructions

This is my personal config — gitignored. Project-wide working notes are in:

- @docs/build-notes.md — operational reference
- @docs/decisions.md — pre-build decisions with reasoning
- @docs/build-readiness.md — pre-build punch list (this should all be done)
- @docs/ai-act-extraction-notes.md — AI Act .txt observations
- @compliance-gap-analysis-spec.md — strategic spec (source of truth)
- @v2_corpus_specification.md — corpus structure and refresh policy

When working on a CAP-ID, read the relevant section of the spec first, then proceed.
```

The `@path` syntax tells Claude Code to load those files as context.

**Acceptance:** Your local `CLAUDE.md` references the docs above. A fresh Claude Code session orients itself in seconds, not minutes.

**Why:** Without this, every fresh session re-derives context from the strategic spec, which is expensive and lossy. With it, your assistant arrives ready.

---

## When all items are checked

You're ready to start ING-01.

The first session begins by reading the strategic spec § ING-01 success conditions, then writing `src/ingestion.py` against them. Your assistant should already know to type chain code against the `LLMClient` ABC, never against `RoutingClient`, because `docs/build-notes.md` says so and CLAUDE.md loaded it.

If you want a low-stakes warm-up before ING-01, write the docstring and one method signature in `src/schema.py` for SCH-01 — the schema is small, fully decided, and gives you a confidence check that the scaffolding works end-to-end.
