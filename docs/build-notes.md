# Build Notes

> Working reference for the implementation phase. Plain-English orientation for fresh sessions — yours or your assistant's. The strategic spec is the source of truth; this doc is the operational layer the spec deliberately doesn't carry.

## Where we are

Pre-build. Spec frozen, corpus assembled and hashed, dependencies pinned, no implementation yet.

**Phase scope (D-007 amended):** build only. Gold-set construction, three-layer evaluation, and error analysis are deferred to a separate evaluation phase that begins after the build-completion gate.

## Where to look

| Doc | Purpose |
|---|---|
| `compliance-gap-analysis-spec.md` | Strategic spec — capabilities, success conditions, FLEX paths, gates. Read first. |
| `v2_corpus_specification.md` | Corpus structure, sources, refresh policy. |
| `requirements.txt` | Pinned dependencies. |
| `corpus/manifest.json` | SHA-256 hashes + per-file provenance. |
| `docs/decisions.md` | Open decisions with suggested values + reasoning. |
| `docs/build-readiness.md` | Pre-build punch list — items to complete before ING-01 starts. |
| `docs/ai-act-extraction-notes.md` | AI Act `.txt` quality observations + article-boundary sketch. |

If this doc and the spec disagree, **the spec wins** — fix this doc.

## Repo layout

```
compliance-gap-analysis/
├── compliance-gap-analysis-spec.md     strategic spec (frozen)
├── v2_corpus_specification.md          corpus spec
├── requirements.txt                    pinned deps
├── .env.example                        env var template
├── corpus/                             frozen corpus + manifest
├── docs/                               working references
├── src/
│   ├── ingestion.py                    ING-01..03
│   ├── retrieval.py                    RET-01..02
│   ├── schema.py                       SCH-01
│   ├── chain.py                        CHN-01..07
│   ├── llm/
│   │   ├── client.py                   LLM-01 (LLMClient ABC)
│   │   ├── base.py                     LLM-02 (BaseLLMClient + task methods)
│   │   ├── adapters.py                 LLM-03 (Llama, Gemma)
│   │   ├── prompts.py                  LLM-04 (prompt registry)
│   │   ├── routing.py                  LLM-05 (RoutingClient)
│   │   └── cache.py                    LLM-06 (disk cache)
│   └── ui/
│       ├── streamlit_app.py            UI-01
│       └── notebook.ipynb              UI-02
└── tests/
    ├── test_smoke.py                   LLM-07
    └── test_typing.py                  LLM-08
```

Every module's first line cites the CAP-ID(s) it implements (`"""ING-01, ING-02, ING-03"""`). This is the contract between spec and code — markers can trace spec→code in 30 seconds, and you can defend it in viva.

## Decisions already made

These come from the strategic spec. Changing them means revisiting the spec and recording a new decision (D-009, D-010, …), not editing here ad-hoc.

- **FLEX-6 typing discipline.** Chain code uses `LLMClient` (the abstract base class), never `RoutingClient` or a concrete adapter directly. Mocks in tests implement the ABC, never subclass routing. `tests/test_typing.py` enforces this mechanically.
- **No LangChain, Chroma, Pydantic, RAGAS, LLM-as-judge.** Each is a deliberate choice (D-004), defendable in viva. Reintroducing any reopens scope.
- **Hardcoded routing policy.** `RoutingClient` handles three exception types (rate-limit, network, schema-parse) with three fixed actions. Configurability would be unused machinery.
- **Cache key includes `model_id`.** Different models never share cached outputs. Required for eval-phase replay determinism.
- **Schema is frozen at 9 fields (SCH-01).** Field changes go through the schema-frozen gate, not ad-hoc edits during chain implementation.
- **Provenance fields are populated post-LLM by chain code.** `regulation_chunk_ids` and `confidence` never appear inside prompts.
- **Silence is a retrieval property, not an LLM judgment.** When `max_sim < τ`, the obligation is classified `silent` deterministically, no LLM call. (D-008.)
- **`gap_characterisation` is descriptive, not prescriptive.** Fork A discipline. The synthesise prompt asks "what's unaddressed?" — not "what should the deployer do?".

## Active gates

| Gate | Triggered by | Pass criteria |
|---|---|---|
| Corpus frozen | Before ING-01 starts | `manifest.json` complete, hashes verified, §8 validation green |
| Retrieval-config freeze | RET-01 + RET-02 functional, before CHN-02 wires up | Embedding model decided, aggregation mode decided, τ spot-check passed, AI Act PDF spot-check passed, ≥60% top-5 recall on 5 hand-written queries |
| Schema frozen | Before CHN-05 and UI-01 consume SCH-01 | SCH-01 9 fields finalised, validates on both backends |
| Extraction-quality | After CHN-03 first wired end-to-end | ≥80% obligations ≥8 words with verb (30-sample); verbatim-appearance ≥9/10 (10-sample) |
| Build-completion Stage 1 | After CHN-05 produces registers on both backends | 5 hand-written queries produce structurally valid registers; cross-contamination check passes |
| Build-completion Stage 2 | After UI-01 functional (or UI-02 fallback active) | End-to-end demo path works; cache pre-warming verified |

Eval phase begins after Stage 2.

## FLEX paths — quick map

| FLEX | Trigger | Action | Cost |
|---|---|---|---|
| FLEX-1 | Cross-contamination on ≥2 of 5 queries (build) or >15% on gold-set (eval) | Per-obligation classifier instead of batched | Refactor 1 function |
| FLEX-2 | Gold-set silence-recall <70% AND false-address >5% | Adaptive τ: (a) lower; (b) per-corpus; (c) distribution-based; (d) threshold+LLM-verify | (a)→(d) increasing |
| FLEX-3 | Retrieval-config freeze gate underperforms | Sentence aggregation `mode='max'` first, then `'mean'`, then swap to `bge-large-en-v1.5` | Cheap → moderate |
| FLEX-4 | Need additional schema field | Add field; update synthesise prompt + UI renderer; chain logic untouched | ~1 hour |
| FLEX-5 | Significant build budget lost (≥1 capability cluster slipping past its dependents) | Drop CHN-03 (obligation extraction); revert to chunk-vs-chunk classification; **keep silence-by-threshold** | Primary scope-cut lever |
| FLEX-6 | Once dual-backend reliability is demonstrated and the eval surface no longer needs Gemma | Strip routing.py + unused adapter + family-keyed prompts (~150 lines); ABC + base class + cache + smoke test stay | ~30 min |

**Priority under time pressure:** FLEX-5 first (most build time saved per unit of complexity removed; preserves the distinctive claim). FLEX-6 strip-down second. FLEX-3 swap is a recall-improvement lever, not a time-saver.

## What NOT to do

- Don't draft prompts in advance of the chain step that consumes them. Prompts get tuned against real chain output; pre-writing locks in imaginary output shapes.
- Don't pre-empt FLEX-3 — the embedding model decision lives at the retrieval-config freeze gate.
- Don't add fields to SCH-01 ad-hoc. Schema changes go through the gate.
- Don't make `RoutingClient` policy configurable. Three exceptions, three actions, hardcoded.
- Don't introduce LLM self-assessment for `confidence`. Retrieval similarity only (D-004 / N-004 discipline).
- Don't let provenance fields leak into prompts. They're populated post-LLM by chain code.
- Don't mix model outputs in the cache. Cache key includes `model_id`.
- Don't write structured logging. Verbose-mode print statements (CHN-06) are the full observability story for the build.
- Don't expand the corpus mid-build. Per v2 §7, corpus changes warrant a versioned snapshot, never in-place edits.

## How to run

Filled in as code lands.

```bash
# Setup (once)
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY

# Smoke test (once LLM-07 is wired)
pytest tests/test_smoke.py

# Streamlit demo
streamlit run src/ui/streamlit_app.py

# Jupyter fallback
jupyter notebook src/ui/notebook.ipynb
```

## Cache locations

All gitignored. Re-runs hit the cache.

- `embeddings/` — sentence-transformer chunk embeddings
- `llm_cache/` — LLM responses, keyed on `(rendered_prompt, model_id)`
- `cache/` — generic caches (token estimates, intermediate scores)

## Recording new decisions

When something gets decided during build:

1. Move from "open" to "decided" in `docs/decisions.md`.
2. Update this doc only if the decision changes one of the architectural commitments above.
3. If the decision is structural enough, give it a label (D-009, D-010, …) and add a one-line note to the strategic spec's decision history.

## Anonymity

Code, comments, and committed docs use student registration number only — no personal name. Personal Claude Code instructions (`CLAUDE.md`) stay gitignored for the same reason.
