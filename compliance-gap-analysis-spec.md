# AI Compliance Gap Analysis
> format: strategic-spec | version: 1.0

A senior compliance lead at Novara AI — a fictive mid-size EU/UK AI company — needs to know whether TalentLens, Novara's CV-screening product, complies with the EU AI Act (Annex III §4 high-risk AI) and UK/EU GDPR (notably Article 22 on automated decision-making). Today this is manual work: read the regulation, read the deployer's published AI policy, read the operational artefacts (DPIA, Model Card, Transparency Notice, Annual Governance Report, Model Intake Assessment), and spot the gaps where the policy says nothing, says too little, or contradicts the regulation. It's slow, error-prone, and expensive when delegated to outside counsel. The EU AI Act came into force in 2024 and organisations are scrambling — the fictive scenario stands in for a real corporate compliance need that's broadly recognised as urgent.

The system addresses this by retrieving against four tagged corpora (regulation, ICO operational guidance, deployer policy, deployer-extras) and running a five-step reasoning chain that decomposes the user query, extracts atomic obligations from regulation, performs per-obligation matching against the deployer side with threshold-grounded silence detection, and synthesises a structured residual-risk register. The intellectual contribution is the multi-corpus comparison and the structured synthesis that makes the boundary between regulation and internal policy *visible* — not legal opinion. Scope claim: decision-support, Fork A (gap-surfacing), not legal-opinion or constraint-aware advisory. The work is also an INST0100 master's-project assessment: every architectural choice must be defendable in 5-minute Q&A, and every excluded alternative must appear in the report's "considered alternatives" section.

This spec covers the **build phase only** (D-007 amended). Six in-scope capability clusters: Ingestion, Retrieval, LLM client + caching, the reasoning Chain, the output Schema, and the UI. Gold-set construction, three-layer evaluation, and error analysis are deferred to a separate evaluation phase that begins after the build is verified working end-to-end on 5 hand-written test queries — this remains a project deliverable but exits the strategic spec. The build is sequenced behind a corpus-frozen gate, a retrieval-configuration freeze gate at end of week 2, a schema-frozen gate, and a two-stage build-completion gate (extraction-quality first, end-to-end second) that triggers the eval phase.

**Stakeholders:**
- Daria — PM / student / sole implementer: owns the assessment, executes the full 8-week build alone within ~12–15 hours/week on consumer hardware and free API tiers; direct, scope-disciplined, pushes back on unnecessary complexity; authored the problem framing, all open questions, and the v2 working doc set.
- Bogdan — planning collaborator active in session-002: co-authored the v2 working docs across multiple iterations and returned in session-002 to stress-test the canvas before crystallisation; pushes for genuine deep reasoning over first proposals, values flexibility and documented backout paths over commitment-to-the-letter; drove the obligation-level chain restructure (D-008), the FLEX-6 model-abstraction shape, the schema chunk-provenance audit, the build-then-eval scope amendment (D-007), the week-7 tutorial-lineage continuity edits, and the Fork A discipline on the organisational-constraints challenge.
- Markers (Arabella Sinclair, Luke Dickens) — implicit assessment stakeholder: assess the deliverable against a rubric (5 dimensions × 20 marks for the 4-page written report; 5 dimensions × 20 marks for the 10-min presentation), reward honest critical analysis and explicit trade-off discussion; every architectural choice and every excluded alternative (LangChain, Chroma, BM25, cross-encoder, Pydantic+structured-output, RAGAS, LLM-as-judge) must be defendable in 5-minute Q&A and present in the report's critical-analysis section.
- Fictive Compliance Officer at Novara — design persona: target user of the system in the fictive scenario, needs to identify policy gaps against regulation, get specific clause-level citations they can hand to legal counsel, and iterate quickly across many compliance questions; persona for design and demo only, no live feedback possible.
- Acknowledged absent perspectives — architect, security reviewer, UX practitioner, domain expert in EU AI Act / GDPR: would have stress-tested dense-retrieval-only adequacy, JSON-in-prompt schema reliability under load, response-cache integrity and API-key handling, residual-risk register cognitive load, and gold-set defensibility against expert correctness; absences acceptable at master's-project scale, honest report mention is the appropriate mitigation.

**Constraints:**
- **Compute & cost:** must run on standard consumer hardware and free API tiers (assessment brief §2.3). No paid managed infrastructure; Groq free tier for primary LLM, Colab GPU for fallback Gemma, Anthropic API for Opus is one-off and outside the production stack.
- **Time:** sole implementer, ~12–15 hours/week across 8 weeks. Cumulative architectural line-count is under pressure against the brief's nominal ~250–400 line budget; FLEX-5 (chain depth collapse) and FLEX-6 strip-down (single-model commitment) are likely-needed scope-cut levers, not theoretical safety.
- **Excluded tooling (D-004):** no LangChain (orchestration is short enough for plain Python), no Chroma / vector store (in-memory NumPy adequate at ~3–5K chunks), no BM25 hybrid retrieval, no cross-encoder reranking, no Pydantic + structured-output libraries (JSON-in-prompt + retry is robust at this scale), no RAGAS / TruLens, no LLM-as-judge (gold set is human-validated, manual scoring on sample is more defensible). Each is documented as a *choice* in the report, not a gap.
- **Anonymity:** report and code use student registration number only; no personal name in artefacts.
- **Pinned dependencies:** `requirements.txt` versions pinned from week 2 to immunise the build against library churn.
- **Scope claim:** Fork A — gap-surfacing decision-support, not legal opinion and not constraint-aware advisory. The system identifies where the policy is silent / partial / contradictory; the human applies organisational constraints. Threshold-grounded silence detection biased toward false-silence (over false-address) is the architectural commitment that keeps the system consistent with this scope claim.
- **Course-material continuity:** the retrieval layer and Jupyter fallback build directly on the INST0100 week-7 RAG practical (Sinclair, Dickens). Adopted patterns: `multi-qa-MiniLM-L6-cos-v1` embedding model, `ChunkEmbeddingRetriever` class shape mirroring the tutorial's `ParagraphEmbeddingRetriever` / `SentenceEmbeddingRetriever`, `util.dot_score` + `torch.topk` retrieval API, spaCy English sentencizer for sub-Article segmentation, mean/min/max aggregation as a FLEX-3 intermediate step, `NewsReader.chat()` loop pattern for the Jupyter fallback, `top_k_accuracy_score` for eval-phase Layer 1 retrieval evaluation.
- **Demo reliability:** dual-backend with automatic fallback (Llama 70B primary via Groq → Gemma 2-2B fallback via Colab); cache pre-warming for planned demo queries; pre-recorded demo video as final safety net.

**Non-goals:**
- **Not legal opinion.** The output is a structured residual-risk register surfacing gaps; the compliance officer takes it to legal counsel. The synthesise-step prompt asks "what's unaddressed?" not "what should the deployer do?" — the field name `gap_characterisation` (not `residual_obligation`) carries this discipline.
- **Not constraint-aware advisory (Fork B).** The system does not reason about organisational risk appetite, sector scrutiny, or budget. Compliance officers apply their own constraints by filtering and sorting on the dimensions the system *does* surface (`match_status`, `confidence`, and — if the deferred severity field lands — `severity`). Fork B alternatives were considered (Alt 3 free-text context note; Alt 4 two-pass `apply_organisational_lens` re-synthesis function; Alt 5 persona-driven prompts) and explicitly not adopted.
- **Not real-world corpus.** Novara / TalentLens are fictive by design (D-001). Real-world depth is replaced by carefully-engineered fictive gaps; controllability gain is judged worth the realism loss.
- **Not corpus assembly, report writing, slide deck, or demo recording in this spec.** Corpus prep is data prep with a checklist already detailed in `v2_corpus_specification.md`. Report and slides/demo are outputs of the work, not capabilities to decompose.
- **Not gold-set construction or three-layer evaluation in this spec (D-007 amended).** These remain project deliverables in the evaluation phase, but do not appear as build-phase capabilities. Eval methodology will be re-derived against the actual D-008 chain output when eval phase begins, not against a pre-build hypothetical.
- **Not LLM-as-judge anywhere.** Gold set is human-validated; manual scoring on a sample is more defensible. `confidence` is derived from retrieval similarity only — no LLM self-assessment, to avoid overlap with the D-004 exclusion.
- **Not a single-model commitment up-front.** The system ships dual-model (D-003); FLEX-6 strip-down is available post-week-4 if a single-model commitment becomes the right call.

**Open questions:**
- **"TalentLens" name confirmation.** Cosmetic. Daria to confirm before final report.
- **Demo persona name.** Optional ("Maya, Head of AI Compliance" suggested). Worth confirming before the 5 hand-written test queries are written for the build-completion gate, since persona choice affects query register.
- **Streamlit colour scheme.** Cosmetic; Novara-blue palette suggested.
- **8-week sequence commitment.** Daria to confirm against her real availability. FLEX-priority triage names FLEX-5 as the primary scope-cut lever if the build runs over.
- **Per-row `sub_question` field for register navigability (deferred design consideration).** When a complex query decomposes into multiple sub-questions in CHN Step 1, the register is currently a flat list of obligation rows; the user can't browse the answer by sub-question structure. A `sub_question: str` field per row would let the UI group/filter rows by sub-question. *Why not now:* solves a different thin spot than chunk provenance (UX/navigability vs audit/verifiability); doesn't earn its keep until a UI exists to consume it. *Cost-of-change:* schema 9 → 10 fields, ~3 lines of chain code (sub-question is already in chain state), Streamlit grouping wrapper, ~30 minutes. *Trigger to revisit:* week-6 Streamlit prototype shows the flat register feels disorienting on multi-sub-question queries, OR demo rehearsal reveals the answer narrative is hard to follow without sub-question structure. *Last-cheap moment:* end of week 6. *Decider:* Daria, at week-6 Streamlit prototype review.
- **Per-row `severity` field for regulatory-weight prioritisation (deferred design consideration).** Two-value enum (`high-risk` / `standard`) populated by chain code post-LLM at Step 3 from a static lookup keyed on `regulatory_provision`. AI Act Annex III + Articles 9–15 + GDPR Article 22 → `high-risk`; other binding GDPR → `standard`. Surfaces regulatory weight per row, enabling Streamlit filter/sort. Stays in **Fork A** (the compliance officer applies their organisational constraints by filtering on severity + `match_status` + `confidence`, rather than the system reasoning about constraints). *Why not now:* the system already surfaces `match_status` and `confidence` as prioritisation dimensions; severity is a third dimension but not strictly necessary for build-completion. *Cost-of-change:* ~60–80 lines split across a `severity_map.py` lookup, a `derive_severity()` function, Step 3 chain integration (~5 lines), Streamlit filter/sort (~20 lines); schema 9 → 10 (or 10 → 11 if `sub_question` lands first); FLEX-6 surface unaffected (severity never enters prompts); ~1–2 hours total. *Trigger to revisit:* eval-phase mid-point shows the system produces many obligations per query and prioritisation feels load-bearing for the report's demo narrative; or marker preview / domain-expert review explicitly asks how the system supports compliance prioritisation; or Daria wants to extend post-submission for portfolio purposes. *Last-cheap moment:* before eval-phase queries are cached. *Decider:* Daria, at eval-phase mid-point. *Other Fork A/B alternatives recorded for if severity isn't the right path:* Alt 2 (UI-only filtering, zero schema change), Alt 3 (optional free-text context note, lightest Fork B), Alt 4 (two-pass `apply_organisational_lens` re-synthesis as natural Fork B), Alt 5 (persona-driven synthesise prompts, fixed-set Fork B).

## Cross-Cutting Concerns

### Reproducibility
Pinned dependency versions in `requirements.txt` from week 2. Embeddings cached deterministically to disk. LLM response cache keyed on `(rendered_prompt + model_id)` hash so different models never pollute each other's cached outputs and so eval-phase replay is deterministic. The corpus has a `manifest.json` with SHA-256 hashes for every file, frozen before ingestion begins. The marker should be able to reproduce results from the artefacts. Cache pre-warming for planned demo queries makes demo latency sub-second under any backend.

### Anonymity
Report uses student registration number only — no name in the report or in code comments. Applies to all artefacts (canvas notwithstanding, which is a working document not a deliverable).

### Rate-limit and network resilience
Dual-backend with automatic fallback is the runtime mechanism. The `RoutingClient` policy is hardcoded: rate-limit error → immediate fallback to Gemma; network error → 1 retry on primary then fallback; schema-parse failure → 1 retry-with-feedback on primary then fallback. If both backends fail (rate-limit + Gemma unavailable, or persistent schema-parse failure on both), the system surfaces a visible error message rather than emitting a malformed register — no silent partial outputs. A pre-recorded demo video is the final safety net for demo-day rate-limit surprises.

### Citation traceability
Every claim in the residual-risk register cites a specific chunk; chunks carry their original source URL via metadata. Schema is symmetric: regulation-side and deployer-side both carry chunk-level provenance. On the regulation side, `regulation_chunk_ids` (added in the session-002 schema audit) records the chunks input to obligation extraction for the sub-question — making *why this obligation exists* auditable in the same way as *why this evidence applies* on the deployer side. The provenance is coarse-grained (the chunks fed to extraction for the sub-question, not surgical per-obligation attribution) — symmetric with how `policy_evidence` / `extras_evidence` / `guidance_evidence` cite chunks on the deployer side, and truthful about what the architecture can attribute.

### Abstention behaviour (structurally grounded — D-008)
Silence is a *retrieval property*, not an LLM judgment. When the maximum cosine similarity of an obligation's embedding against the three deployer-side corpora (Novara policy, deployer-extras, ICO operational guidance) falls below τ, the row is classified `silent` deterministically without any LLM involvement. Identical inputs always produce identical silence verdicts — auditable, explainable, cheap. Per Bogdan's session-002 audit, this is the load-bearing capability for the project's distinctive intellectual claim ("making the boundary between regulation and policy visible") and the architectural commitment that keeps the system consistent with the Fork A scope claim. The UI renders silent rows with an explanatory marker ("no policy chunk above similarity τ").

### Honest scope
System is decision-support, not legal-opinion. This statement appears in the report and in the demo. Threshold-grounded silence detection biased toward false-silence (rather than false-address) makes the architecture consistent with the scope claim — over-flagging is the safer error, false-address (system says "adequate" when policy is silent) is the dangerous failure mode for compliance work. The synthesise-step prompt asks "what's unaddressed?" not "what should the deployer do?" — the field name `gap_characterisation` (not `residual_obligation`) carries this discipline through to the schema. The report's critical-analysis section needs to carry the analytical argument for why threshold-grounded silence detection with conservative bias is a *meaningful operationalisation* of the north-star claim, not a degraded approximation; pre-articulating this is report-side work outside the spec but flagged here so future-Daria doesn't lose the thread when writing.

### Model-knowledge isolation (FLEX-6)
Model-specific knowledge — prompts, JSON-parsing tolerance, transport details, capability limits — lives only in per-model adapters and the `(task, family)`-keyed prompt registry. Parsing tolerance specifically lives in adapters, not in the base class: response cleanup, preamble-stripping, and JSON-extraction quirks vary by model and so belong with the adapter that knows the model's quirks. The base class accepts strings and returns parsed structures; the strings-to-parsed dispatch is per-adapter. The chain, retrieval, schema, evaluation harness, and UI never reference a specific model. Cache keying on rendered prompt + model identifier operationalises this for evaluation reproducibility. The discipline that makes the abstraction safe to strip later (FLEX-6 strip-down): chain code types against the abstract LLM interface, never against the concrete routing wrapper. Mocks in tests implement the ABC, not subclass the routing class — and a typing-discipline mock test mechanically validates this.

### Course-material continuity (week-7 RAG practical lineage)
The retrieval layer and Jupyter fallback build directly on the INST0100 week-7 *Information Retrieval / RAG* practical (Sinclair, Dickens). *Adopted patterns:* `multi-qa-MiniLM-L6-cos-v1` embedding model, `ChunkEmbeddingRetriever` class shape (mirrors `ParagraphEmbeddingRetriever` / `SentenceEmbeddingRetriever`), `util.dot_score` + `torch.topk` retrieval API, spaCy English sentencizer (`spacy.lang.en.English` with `add_pipe("sentencizer")`) for sub-Article segmentation, mean/min/max aggregation modes (recorded in FLEX-3 as the lighter intermediate retrieval-improvement path before the embedding-model swap), `NewsReader.chat()` loop pattern for the Jupyter fallback, `top_k_accuracy_score` from sklearn for eval-phase Layer 1 retrieval evaluation. *Extensions beyond the tutorial:* multi-corpus retrieval over four buckets, LLM generation per the Task-3 extension hint, the 5-step obligation-level reasoning chain (D-008), 9-field structured output schema with `regulation_chunk_ids` provenance, threshold-grounded silence detection, 4-state classification, LLM client abstraction with FLEX-6. The tutorial provides the foundation; the project's distinctive contribution is the superstructure. Pedagogical traceability earns marker engagement for "what's foundation vs what's contribution" without diluting the project's distinctive claim.

### Compute constraint
Must run on standard consumer hardware or free API tiers (assessment brief §2.3). In-memory NumPy retrieval at ~3–5K chunks; Llama 70B served via Groq free tier (rate-limit-managed by the routing layer); Gemma 2-2B served on Colab GPU as the fallback (no rate limits, no network dependency on Groq). Anthropic API access for Opus gold-set bootstrap is a separate, one-off, eval-phase pre-condition — flagged here so future-Daria doesn't discover this at week-5 with no API key set up.

### Active tension — T-005 silence-detection calibration thinness vs distinctive-claim load-bearing (half-resolved)
Silence detection is the load-bearing capability for the project's distinctive intellectual claim, but the gold set has only ~8–12 silence cases — statistically too thin to calibrate τ tightly. **Build-time resolution (D-007 amended):** ship with conservative high default τ = 0.35 for the entire build phase, biased toward false-silence over false-address; *no calibration during build*; build-time silence behaviour expected to appear over-zealous on the 5 hand-written test queries (this is the conservative default doing its job, not a defect — do not lower τ based on hand-written-query intuition). A *τ corpus-specific spot-check* is bundled into the end-of-week-2 retrieval-configuration freeze gate: similarity histogram of a sample of obligations against deployer corpora to verify τ = 0.35 sits in a meaningful position relative to the actual cosine distribution on legal text. If the median max-sim sits near or above 0.35, raise τ rather than ship a default that flags everything as silent. This is a sanity-floor check, not calibration. **Eval-phase resolution (deferred):** empirical calibration against gold-set silence cases when eval phase begins; honest report-side reporting; escalation paths recorded in FLEX-2 (per-corpus τ → distribution-based threshold → threshold-then-LLM-verify) if calibration falls short.

### Architecture flex points (six, with documented swap triggers and cost-of-change)
- **FLEX-1 — Classification flavor:** batched (default) ↔ per-obligation (escalation). Step 4's classifier prompt currently batches obligations within a sub-question. Escalation is one classifier call per obligation. Cost to swap: refactor a single function; prompt template largely reused. Triggers (either fires escalation): build-time manual inspection at the build-completion Stage-1 gate finds cross-contamination on ≥ 2 of the 5 hand-written queries; eval-phase cross-contamination rate > 15% on gold-set obligation-level audit.
- **FLEX-2 — Silence threshold τ:** global default ↔ adaptive. Adaptive options in priority order: (a) lower τ slightly; (b) per-corpus τ (separate floors for policy / extras / ICO); (c) distribution-based threshold (max-sim vs corpus mean+kσ); (d) threshold-then-LLM-verify. Implementation cost increases (a)→(d). Trigger: gold-set silence-recall < 70% combined with false-address rate > 5%.
- **FLEX-3 — Embedding model:** `multi-qa-MiniLM-L6-cos-v1` (default) ↔ `bge-large-en-v1.5`. Decided at the end-of-week-2 retrieval-configuration freeze gate. Lighter intermediate step before swapping the embedding model: sentence-level retrieval with mean/min/max aggregation modes (try `mode='max'` first, fall back to `mean` for noise-robustness). Two additional checks bundled into the gate: τ corpus-specific similarity histogram on legal text; AI Act PDF extraction spot-check (5–10 chunks manually reviewed for cross-references / footnotes / recitals diluting semantic signal).
- **FLEX-4 — Schema field set:** nine fields are canonical. Adding (e.g., `severity`, `sub_question`) or removing (e.g., merging `policy_evidence` + `extras_evidence` if extras stay sparse) is isolated to schema definition + synthesis prompt + UI renderer. No retrieval/chain logic touched. Provenance fields like `regulation_chunk_ids` are populated by chain code post-LLM and never appear in prompts — adding similar metadata fields doesn't expand the FLEX-6 prompt-tuning surface.
- **FLEX-5 — Reasoning chain depth:** minimum-viable collapse path. Drop Step 3 (obligation extraction), revert Step 4 to chunk-vs-chunk classification, *keep silence-by-threshold as a deterministic check on retrieval*. The 4-state classification survives even at minimum chain depth. Trigger: more than 1 week of build budget lost to upstream issues. Note: invocation of FLEX-5 during build shifts eval-phase methodology — gold queries with chunk-level expected outputs rather than per-obligation rows.
- **FLEX-6 — LLM model/provider swap and strip-down:** the abstraction isolates model-specific knowledge inside per-model adapters. Adding a new model: ~50-line adapter + 4 prompt entries + smoke test. ~3–5 hours including prompt tuning. **Strip-down path:** post-week-4 commitment to one model — `routing.py`, the unused adapter, family-keyed prompts and parsing branches (~150 lines) all cleanly removable; the ABC, base class task methods, prompt registry, smoke test, and cache keying stay (prompt-hygiene infrastructure). Cost: ~30 minutes.
- **FLEX-priority triage under time pressure:** FLEX-5 is the primary scope-cut lever (absorbs the most build time per unit of complexity removed and preserves silence-by-threshold). FLEX-6 strip-down is secondary (removes routing layer + one adapter at the cost of demo-day reliability fallback). FLEX-3 embedding swap is tertiary (typically a recall-improvement lever rather than a time-saver). FLEX-1, FLEX-2, FLEX-4 are configuration tunings, not scope cuts.

## Group: Ingestion
> priority: must-have

Loads the four-bucket corpus (regulation, ICO operational guidance, deployer policy, deployer-extras) into typed chunk records that downstream retrieval, the chain, and citations can reference. ING is the foundational layer — without truthful chunk metadata and stable chunk IDs, citation traceability fails everywhere. The group exists to deliver one outcome: a deterministic, hashed, embedded chunk store that retrieval can query against, with article/§-bounded structural integrity preserved on legal texts and tutorial-faithful sentence segmentation within larger structural units. Standalone value of completing the group: a corpus that can be loaded, inspected, and embedded reproducibly — sufficient to stand up retrieval against it as the next step.

### ING-01: Typed chunk loading from four-bucket corpus
> priority: must-have | risk: low
> depends_on: -

Loads PDF / HTML / text source files for the four corpora — EU AI Act + UK/EU GDPR articles (regulation), ICO AI guidance (operational guidance), Novara published AI policy (deployer policy), Novara DPIA / Model Card / Transparency Notice / Annual Governance Report / Model Intake Assessment (deployer-extras) — into typed chunk records that carry corpus tag, document ID, section reference, source URL, and chunk text. The output supports downstream retrieval filtering by corpus bucket (the four-bucket architecture is a load-bearing distinction: regulation chunks are extracted *from* in CHN Step 3; deployer-side chunks are matched *against* in CHN Step 4 silence detection). Ingestion runs once over a frozen corpus (the CORP-frozen gate is a hard pre-condition: `manifest.json` with SHA-256 hashes per file must exist before ING runs), so this is a batch operation, not a streaming pipeline. The `manifest.json` produced by the corpus assembly track is an input, not an output; this capability consumes the manifest and emits chunk records that downstream code can hash against the manifest for reproducibility.

**Success conditions:**
- All 50–80 expected chunks from the frozen corpus load without error.
- Sample chunks (manually inspected) contain coherent text — no obvious extraction noise that would compromise embedding quality (e.g., garbled PDF cross-references, dropped section numbering).
- Every chunk record carries corpus tag, document ID, section reference (e.g., "GDPR Art 22(3)"), source URL, and the chunk text — verifiable by inspection of any chunk.
- Total ingestion completes in under 60 seconds on standard consumer hardware.
- Chunk IDs are stable across re-runs against the same `manifest.json` — re-running ingestion produces identical chunk IDs (precondition for cache reproducibility).

### ING-02: Article/§-bounded structural chunking with sentence segmentation
> priority: must-have | risk: medium
> depends_on: ING-01

Chunks legal texts (EU AI Act, UK/EU GDPR articles) along their structural boundaries — Article and § level — because legal-text structural integrity matters for citation traceability (a marker should be able to read "GDPR Art 22(3)" on a register row and find the cited chunk). Within larger structural units, applies sentence segmentation via spaCy's English sentencizer (`spacy.lang.en.English` with `add_pipe("sentencizer")`) — adopting the tutorial week-7 `SentenceEmbeddingRetriever` chunking pattern for course-material continuity. The capability sits in the middle of risk landscape #5 and #11: `multi-qa-MiniLM-L6-cos-v1` is the course default but may have weak recall on dense legal text, and the embedding distribution on legal text (cosine distributions on EU AI Act + GDPR text) is unvalidated. Article-level chunks may be long enough that single-vector chunk embeddings dilute relevant sub-sentence content; the FLEX-3 escalation path (mean/min/max aggregation modes before embedding-model swap) is a cheaper recovery than re-chunking, but baseline chunking has to leave aggregation a usable option — that's why sentence boundaries are preserved at this layer.

**Success conditions:**
- Regulation chunks respect Article / § boundaries — no chunk straddles two Articles, verifiable on a manual inspection of 5 chunks.
- Within larger structural units (e.g., long Articles), chunks are split at sentence boundaries — no mid-sentence breaks on a manual inspection.
- The AI Act PDF extraction spot-check at the end-of-week-2 retrieval-configuration freeze gate (5–10 manually reviewed chunks) confirms cross-references, footnotes, and recitals haven't diluted semantic signal beyond usable thresholds.
- Sentence-level granularity is preserved in chunk metadata so the FLEX-3 aggregation-mode intermediate step is available without re-chunking.

### ING-03: Chunk embedding with on-disk cache
> priority: must-have | risk: low
> depends_on: ING-02

Embeds every chunk with `multi-qa-MiniLM-L6-cos-v1` (the course default; FLEX-3 swap to `bge-large-en-v1.5` is decided at the end-of-week-2 retrieval-configuration freeze gate) and caches embeddings to disk so the embedding step doesn't run on every system start. Cache keying must allow cache invalidation when the embedding model changes (FLEX-3 invocation should not silently reuse stale `multi-qa-MiniLM` embeddings as if they were `bge-large` embeddings). Embedding completion under 3 minutes is the success bar for the build; faster is welcome. This capability is the input to all retrieval — RET-01 reads from the embedding cache, not from re-embedding live.

**Success conditions:**
- All chunks from ING-02 are embedded with `multi-qa-MiniLM-L6-cos-v1` (or the FLEX-3-swapped model) and cached to disk.
- Total embedding completes under 3 minutes on standard consumer hardware.
- Re-running embedding against the same chunks + same model hits the cache rather than re-embedding (verifiable by timing).
- Cache invalidates correctly when the embedding model changes (FLEX-3 swap does not reuse stale embeddings).

## Group: Retrieval
> priority: must-have

Provides the multi-corpus retrieval interface that the chain (CHN) reads against — both Step 2 (retrieve regulation chunks for each sub-question) and Step 4 (retrieve deployer-side evidence per obligation, plus the silence-detection cosine check). RET is the chain's sole dependency on the corpus; making it model-blind and tutorial-faithful means the chain doesn't know anything about embedding models or chunk storage. Standalone value of completing the group: a class that, given a query and a corpus filter, returns top-k chunks with similarity scores — enough to verify retrieval recall on the 5 hand-written test queries before any chain logic is built. The end-of-week-2 retrieval-configuration freeze gate is the boundary between RET and CHN: embedding model decided (FLEX-3), aggregation mode decided, τ corpus-specific spot-check passed.

### RET-01: Multi-corpus chunk-level retriever
> priority: must-have | risk: medium
> depends_on: ING-03

The retriever class (conceptually mirroring the tutorial week-7 `ParagraphEmbeddingRetriever` / `SentenceEmbeddingRetriever` shape, extended for the four-bucket architecture) accepts a query plus an optional corpus filter and returns top-k chunks with similarity scores. The filter is the load-bearing extension over the tutorial pattern: CHN Step 2 needs regulation chunks only, CHN Step 4 needs deployer-side chunks only (policy / extras / guidance) for silence detection. Cosine similarity via `util.dot_score` from `sentence_transformers.util` (equivalent to NumPy cosine for unit-norm embeddings); top-k selection via `torch.topk`. The capability also supports the retrieval similarity threshold for system abstention — the cosine values returned here are what D-008's silence detection thresholds against. The week-2 retrieval-configuration freeze gate is where this capability is verified against the 5 hand-written test queries (≥ 60% expected chunks in top-5) before any chain logic is added. Risk is medium because of risk landscape #5 + #11: dense-only retrieval on legal text is unvalidated for this corpus; FLEX-3 escalation paths exist (aggregation modes first, embedding swap second).

**Success conditions:**
- Retrieval against the full corpus (post-ING-03) returns top-5 in under 200 ms.
- Five hand-written test queries each return ≥ 60% of expected chunks in their top-5.
- Per-corpus filtering verifiably restricts results to the requested corpus tag (e.g., regulation-only filter returns no policy chunks).
- The retriever exposes raw cosine similarity scores per chunk so CHN-04 can apply the silence threshold τ deterministically.
- The end-of-week-2 retrieval-configuration freeze gate passes: embedding model decided (FLEX-3), aggregation mode decided (mean/min/max if invoked), τ corpus-specific similarity histogram confirms τ = 0.35 sits in a meaningful position relative to actual cosine distribution on legal text, AI Act PDF extraction spot-check passes.

### RET-02: Sentence-level aggregation modes (FLEX-3 intermediate)
> priority: should-have | risk: medium
> depends_on: RET-01

Sentence-level retrieval with mean / min / max aggregation modes — adopting the tutorial week-7 `SentenceEmbeddingRetriever` aggregation pattern. Recorded as a FLEX-3 intermediate step before any embedding-model swap: if Article-level chunks are long enough that single-vector chunk embeddings dilute relevant sub-sentence content, aggregation may recover recall without needing to switch embedding models entirely. Try `mode='max'` first (best-sentence wins); fall back to `mean` for noise-robustness; reserve embedding-model swap for cases where neither aggregation mode recovers recall. The capability is `should-have` because it earns its keep only if RET-01 underperforms on the 5 hand-written test queries at the freeze gate — but if it's needed, it must be available *before* the freeze gate decision is made (otherwise FLEX-3 collapses to "swap embedding model" with no intermediate step).

**Success conditions:**
- Aggregation mode is configurable per-call: `mode='max'` and `mode='mean'` both runnable on the same retriever interface.
- On the 5 hand-written test queries, switching from chunk-level to `mode='max'` aggregation produces a measurable change in retrieval similarity scores (validating the mechanism is wired up — not a quality bar at this stage).
- The capability is exercised at the end-of-week-2 freeze gate decision if RET-01's chunk-level retrieval underperforms.

## Group: LLM Client and Caching
> priority: must-have

The model-blind LLM subsystem. Three concrete pieces, one prompt registry, one routing wrapper. Delivers a typed task-shaped interface (decompose, extract obligations, classify obligations, synthesise register) that the chain calls without knowing which model is behind it — and a disk-cached transport that makes repeated runs cheap. The group is the home of FLEX-6 (model swap, strip-down to single-model). Standalone value of completing the group: any of the chain's task methods can be called against a smoke-test query and produce structurally valid output on both backends with cache-warm latency under a second. The architectural commitment recorded in D-008's session-002 addendum is preserved: ~420 lines across 6 files, no LangChain, no Pydantic, no plugin discovery, hardcoded routing policy.

### LLM-01: Abstract LLM interface (LLMClient ABC)
> priority: must-have | risk: low
> depends_on: -

Defines the model-blind interface that all chain code types against. Three properties (`model_family`, `model_id`, `max_context`) and one abstract method (`_complete(prompt) -> str`). This is the type that mocks in tests must implement and that chain variables must be annotated against — never against the concrete routing wrapper, never against a per-model adapter. The discipline is what makes FLEX-6 strip-safe: as long as chain code types against the ABC, the routing layer is swap-out-able for any concrete adapter. The typing-discipline mock test (LLM-07) mechanically validates this. This is a small but architecturally load-bearing capability — it costs almost nothing to define correctly and almost everything to retrofit later.

**Success conditions:**
- The ABC defines `model_family`, `model_id`, `max_context` as properties and `_complete(prompt) -> str` as the only abstract method.
- A mock object implementing only the ABC's surface (not subclassing the routing wrapper or any adapter) can be passed to chain code and run end-to-end (validated by LLM-07).
- All chain variables that hold an LLM client are typed against this ABC.

### LLM-02: BaseLLMClient with concrete task methods
> priority: must-have | risk: low
> depends_on: LLM-01

Concrete task methods (`decompose_query`, `extract_obligations`, `classify_obligations`, `synthesise_register`) that look up prompts from the registry keyed on `(task, family)`, call `_complete()`, and parse output with family-appropriate tolerance. The concrete-on-base-class shape (rather than abstract on the ABC) is a deliberate D-008 addendum decision: if task methods were abstract, every adapter would have to reimplement them, fragmenting prompt logic across files and pulling adapters from ~50 lines each up to ~150. With concrete task methods on the base class, adapters implement `_complete()` only and get task methods for free. Task-shaped (rather than generic `complete(prompt) -> str`) is also deliberate — it keeps prompt knowledge out of the chain. This earns its keep even if Daria commits to a single model later (FLEX-6 strip-down preserves these task methods; they're prompt-hygiene infrastructure, not multi-model machinery).

**Success conditions:**
- The base class exposes the four task methods with stable signatures the chain relies on.
- Each task method looks up its prompt from the registry by `(task, family)` and invokes `_complete()` exactly once per call (modulo retry-with-feedback paths).
- Parsing tolerance for task method outputs lives in adapters, not in the base class — verifiable by code review (the base class accepts strings and returns parsed structures via per-adapter dispatch).

### LLM-03: Per-model adapters (Llama 70B, Gemma 2-2B)
> priority: must-have | risk: medium
> depends_on: LLM-02

Two concrete adapters: `GroqLlama70B` (primary; Groq free tier) and `LocalGemma2B` (fallback; Colab GPU). Each implements `_complete()` only — ~50–60 lines per adapter — plus self-contained transport, auth, and (for Gemma) GPU management. Parsing tolerance specifically lives here, not in the base class: response cleanup, preamble-stripping, and JSON-extraction quirks vary by model and so belong with the adapter that knows the model's quirks. This is the boundary that makes FLEX-6 strip-safe — removing an adapter removes its parsing knowledge with it; adding an adapter doesn't require base-class branching. Risk is medium because of risk landscape #1 (schema drift on Gemma 2-2B) and #10 (Gemma latency on the 5-step chain depends on prompt lengths that are not pre-validated — the 90-second target in the CHN Quality Bar is a working assumption to be confirmed at the week-3 single-model gate).

**Success conditions:**
- `GroqLlama70B` adapter calls Groq's free-tier API with correct auth, returns the model's text completion, and propagates rate-limit / network exceptions in a form `RoutingClient` can catch.
- `LocalGemma2B` adapter loads Gemma 2-2B-it on Colab GPU, runs inference on local tensors, and returns text completion.
- Each adapter parses model output with family-appropriate tolerance — verifiable by smoke test on 5 fixed queries.
- Both adapters pass the LLM-06 smoke test before being used in the chain.

### LLM-04: Prompt registry
> priority: must-have | risk: low
> depends_on: LLM-02

Single Python dict in `prompts.py` keyed on `(task, family)`. No Jinja, no YAML, no plugin discovery — inline-readable, the entire prompt set fits in one file. Deliberate over-engineering rejection from the D-008 addendum audit: per-model retry policies were collapsed to one global policy, capability flags (`supports_json_mode`, `supports_few_shot_well`) were dropped as dead documentation, and separate prompt files / templating engines were rejected as disproportionate at this scale. The registry is the *only* place outside per-model adapters that holds family-specific knowledge — so adding a new model means one new adapter plus four new prompt entries (one per task), no other code changes.

**Success conditions:**
- All four task method names from LLM-02 (`decompose_query`, `extract_obligations`, `classify_obligations`, `synthesise_register`) have prompt entries for both `llama` and `gemma` families.
- Prompts are inline-readable in `prompts.py` — no template rendering layer.
- Adding a new model family requires only adding four entries to the dict (verifiable by FLEX-6 documentation matching the actual code surface).

### LLM-05: RoutingClient with hardcoded policy
> priority: must-have | risk: medium
> depends_on: LLM-03

Wraps primary (Llama 70B) + fallback (Gemma 2-2B) with hardcoded routing policy: rate-limit error → immediate fallback; network error → 1 retry on primary then fallback; schema-parse failure → 1 retry-with-feedback on primary then fallback. ~50 lines. Implements the LLMClient ABC (so the chain doesn't know it's there). Bogdan's session-002 audit collapsed earlier "layered" naming; this is one wrapper class, not an architectural layer. Hardcoded policy was a deliberate decision over configurable policy — at this project scale, the three exception types are known and the right action per type is known; making the policy configurable would be unused machinery. Risk is medium because risk landscape #2 (free-tier rate limits during demo) is the most likely runtime failure mode and `RoutingClient` is the runtime mitigation.

**Success conditions:**
- Forced rate-limit error on the primary triggers immediate fallback to Gemma successfully (verified by induced test).
- Forced network error on the primary triggers 1 retry on primary, then fallback to Gemma (verified by induced test).
- Schema-parse failure on the primary's output triggers 1 retry-with-feedback on primary, then fallback to Gemma.
- If both backends fail (dual-backend failure — rate-limit + Gemma unavailable, or persistent schema-parse failure on both), the system surfaces a visible error message rather than emitting a malformed register (verified by induced test).
- `RoutingClient` is annotated as implementing the LLMClient ABC and chain code never references it directly.

### LLM-06: Disk response cache
> priority: must-have | risk: low
> depends_on: LLM-03

Disk cache keyed on `(rendered_prompt, model_id)`. Different models never pollute each other's cached outputs, and re-runs for evaluation are deterministic. Serves four purposes: rate-limit safety (cache hits don't burn API quota), dev iteration (cache hits are sub-second), demo pre-warming (planned demo queries are pre-warmed and demo latency is sub-second under any backend), evaluation reproducibility (eval-phase replay against the same model produces identical cached outputs). The cache also operationalises the reproducibility cross-cutting concern. *Note:* Opus (gold-set bootstrap script in eval phase) is not routed through this cache — it's a one-off script outside the FLEX-6 abstraction.

**Success conditions:**
- Identical prompts hit the cache on the second call (verifiable by latency or hit indicator).
- Cache survives notebook restart — re-launching the system from cold finds prior cached responses on disk.
- Cache key includes `model_id` so swapping models invalidates the cache for that prompt rather than serving stale outputs from the other model.
- Demo-day pre-warming workflow: running the demo queries once before the demo populates the cache and subsequent demo runs are sub-second.

### LLM-07: Adapter smoke test
> priority: must-have | risk: low
> depends_on: LLM-03, CHN-05

A smoke test that runs 5 fixed test queries through the full chain against an adapter, asserting (a) JSON parses, (b) all classifications fall in the silent / partial / adequate / contradictory enum, (c) every non-silent row carries at least one citation. Runtime under 1 minute on cached calls. New adapters pass this test before being used in evaluation cycles — catches "swap that mechanically works but produces garbage" early, which is the FLEX-6 quality bar. Depends on CHN-05 because it runs end-to-end against the synthesise step.

**Success conditions:**
- Both shipping adapters (`GroqLlama70B`, `LocalGemma2B`) pass the smoke test before week-3 single-model gate.
- Test runtime under 1 minute when LLM responses are cache-warm.
- Test fails loudly (with a diagnostic) if any of the three assertions break — JSON parse, enum membership, citation presence.

### LLM-08: Typing-discipline mock test (FLEX-6 strip-safety)
> priority: should-have | risk: low
> depends_on: LLM-01, CHN-05

A test fixture that supplies a mock `LLMClient` (implementing the ABC directly, *not* subclassing the routing wrapper or any adapter) into the chain and verifies the chain runs end-to-end against the mock. Mechanically validates the FLEX-6 strip-safety discipline — chain code types against the abstract interface, never against the concrete routing class. Without this test, the strip-safety claim is documented but not enforced; with it, any future code change that types against `RoutingClient` directly will fail the test. `should-have` rather than `must-have` because it's a discipline-enforcement mechanism rather than runtime functionality, but its absence has been called out as architecturally load-bearing in the FLEX-6 strip-down rationale.

**Success conditions:**
- A mock implementing the LLMClient ABC (not subclassing `RoutingClient` or any adapter) can be passed to the chain and the chain runs end-to-end against it.
- The test fails if chain code is refactored to type against `RoutingClient` directly.
- Test runtime under 30 seconds.

## Group: Reasoning Chain
> priority: must-have

The five-step obligation-level reasoning chain that produces the residual-risk register. The unit of comparison is the *atomic obligation*, not the chunk (D-008 — the architectural correction in session-002). Step 1 decomposes the user query, Step 2 retrieves regulation chunks for each sub-question, Step 3 extracts atomic obligations from the regulation chunks, Step 4 performs per-obligation matching with threshold-grounded silence detection plus a batched 4-state classifier, Step 5 synthesises the register from per-obligation rows. Cost per uncached query: ~6–8 LLM calls. The group is the system's intellectual contribution — every other group exists in service of the chain. Standalone value of completing the group: a single function that takes a user query and produces a structured register on cached LLM calls, runnable end-to-end on both backends.

The chain threads structured per-obligation state through Steps 3–5. Each obligation carries (at minimum): its extracted text, the sub-question it belongs to, the regulation chunk IDs it was extracted from, its match_status once classified, and references to evidence retrieved during matching. The exact data structure (dataclass, dict, etc.) and field types are implementation choices left to the builder. What the spec commits to is the *contract* between Step 3's output and Step 5's input: enough state must propagate that Step 5 can populate every schema field without re-querying.

### CHN-01: Step 1 — Query decomposition
> priority: must-have | risk: low
> depends_on: LLM-02, LLM-04

Decomposes the user's compliance query into focused regulatory sub-questions (1 LLM call). The `decompose_query` task method on `BaseLLMClient` is the entry point. Each sub-question becomes the unit that Steps 2–4 operate on, so decomposition shape directly affects retrieval focus, extraction quality, and the register's narrative arc. A typical 3-sub-question decomposition is the working assumption for the cost calculation (~6–8 LLM calls per query). Sub-question identity is part of the chain state threaded through Steps 3–5 — this is what makes the deferred `sub_question` schema field cheap if it's later triggered (the data is already in chain state).

**Success conditions:**
- Each of the 5 hand-written test queries produces a list of focused sub-questions (≥ 1) on the first cache-miss call.
- Sub-question identity (its index or label) is propagated through chain state to Steps 2–5 so it can be referenced when populating the register.
- Decomposition output parses cleanly on both Llama and Gemma backends (verifiable by smoke test).

### CHN-02: Step 2 — Per-sub-question regulation retrieval
> priority: must-have | risk: low
> depends_on: CHN-01, RET-01

For each sub-question from Step 1, retrieves regulation chunks via `RET-01` with a regulation-only corpus filter (no LLM call). The retrieved chunk IDs are recorded in chain state — not in prompts — so they can be threaded to Step 3 for obligation extraction and to the schema's `regulation_chunk_ids` field at Step 5 row construction. This is the load-bearing connection between retrieval and the chain: the retrieval-configuration freeze gate at end of week 2 must pass before this step is exercised, because retrieval recall on regulation here drives extraction quality at Step 3.

**Success conditions:**
- For each sub-question, top-k regulation chunks are retrieved with their similarity scores.
- Chunk IDs are recorded in chain state, never in prompts (verifiable by code review of the extraction prompt).
- Regulation-only corpus filtering is enforced (no policy / extras / guidance chunks leak through).

### CHN-03: Step 3 — Atomic obligation extraction
> priority: must-have | risk: high
> depends_on: CHN-02, LLM-02, LLM-04

For each set of regulation chunks from Step 2, extracts atomic obligations via the `extract_obligations` task method on `BaseLLMClient` — 1 LLM call per sub-question, output is a list of atomic obligation strings (cap ~5 per sub-question). This is the architectural correction from D-008: by extracting obligations as the unit of comparison rather than synthesising chunk-vs-chunk, silence on a specific obligation becomes structurally visible downstream. **Risk is high** because (i) vague obligations would corrupt downstream classification (a new failure mode introduced by D-008 — e.g., "comply with Article 22" is too thin to retrieve against meaningfully); (ii) extraction quality determines whether silence detection at Step 4 is actually meaningful; (iii) Bogdan flagged this in session-002 as the architectural commitment most exposed to the gold-set thinness on silence cases. Risk is mitigated by the front-loaded mid-week-3 manual review (extraction-quality gate, ≥ 80% obligations ≥ 8 words with verb on 30-sample) plus the verbatim-appearance invariant (≥ 9/10 on a 10-row sub-sample), and by FLEX-5's collapse path (drop Step 3 entirely while keeping silence-by-threshold).

**Success conditions:**
- Each sub-question's regulation chunks produce a list of atomic obligation strings (cap ~5 per sub-question) on the first cache-miss call.
- Extraction-quality manual gate at mid-week-3: ≥ 80% of extracted obligations average ≥ 8 words and contain at least one verb, on a manually-checked sample of 30 obligations from the 5 hand-written test queries.
- Verbatim-appearance invariant on a 10-row sub-sample of the same 30: extracted obligation text overlaps meaningfully with at least one cited regulation chunk. Acceptance ≥ 9/10. Build-time hallucination-detection proxy.
- Each extracted obligation carries the regulation chunk IDs it was extracted from, in chain state, so Step 5 can populate `regulation_chunk_ids` without re-querying.
- If extraction quality fails the gate, FLEX-5 invocation path is available (drop Step 3, revert to chunk-level classification, keep silence-by-threshold).

### CHN-04: Step 4 — Per-obligation matching with threshold-grounded silence detection
> priority: must-have | risk: high
> depends_on: CHN-03, LLM-02, LLM-04, RET-01, SCH-01

Per-obligation matching runs in two phases. **Phase 1 (silence detection, no LLM):** embed each obligation locally with the same sentence-transformer used by retrieval (~5ms per obligation; no API call), compute max cosine similarity against the three deployer-side buckets (Novara policy, deployer-extras, ICO operational guidance) via `RET-01`. If max sim < τ (default τ = 0.35), classify the obligation `silent` deterministically — no LLM call, no LLM judgment. Log the obligation's `max_sim` and `τ` for build-time observability (CHN-06 verbose mode). **Phase 2 (4-state classification, LLM):** for surviving obligations, one batched classifier call per sub-question (the `classify_obligations` task method on `BaseLLMClient`) takes the obligations list + retrieved evidence and outputs status (silent / partial / adequate / contradictory) per obligation with citations. Default flavor is batched (D-008: cheaper at runtime, ~6 calls per query vs ~18, without changing silence-detection accuracy because silence is detected pre-LLM). Per-obligation classification is the documented FLEX-1 escalation. **Risk is high** because of T-005 (silence detection is the load-bearing capability for the project's distinctive intellectual claim, but the gold set has only ~8–12 silence cases; build-time silence behaviour will appear over-zealous on the 5 hand-written test queries — this is the conservative default doing its job, not a defect) and because of cross-contamination latent risk in the batched classifier (FLEX-1 build-time trigger: cross-contamination on ≥ 2 of 5 hand-written queries triggers per-obligation escalation).

**Success conditions:**
- Phase 1 silence detection: each obligation's max cosine similarity against the three deployer corpora is computed and compared to τ; if max sim < τ, obligation is classified `silent` with no LLM call.
- Across the 5 hand-written test queries, verbose mode shows at least one obligation-level SILENT determination with logged `max_sim` and `τ` values visible. (Build-time correctness check that the threshold mechanism is firing — not a calibration check.)
- Phase 2 classification: surviving obligations receive one of `partial` / `adequate` / `contradictory` from a batched classifier call per sub-question, with citations to specific deployer-side chunks.
- All four classifications fall within the enum (silent / partial / adequate / contradictory) — verified by smoke test on both backends.
- Cross-contamination manual inspection of 3 random non-silent rows from 3 different hand-written queries: cited policy/extras/guidance evidence is plausibly related to the row's obligation text. Contamination on ≥ 2 queries triggers FLEX-1 escalation to per-obligation classification.
- The end-of-week-2 freeze gate τ corpus-specific spot-check passes (similarity histogram confirms τ = 0.35 sits in a meaningful position on legal text).
- `confidence` is derived from retrieval similarity only — no LLM self-assessment (D-004 / N-004 discipline).

### CHN-05: Step 5 — Register synthesis from per-obligation rows
> priority: must-have | risk: medium
> depends_on: CHN-04, SCH-01, LLM-02, LLM-04

Synthesises the residual-risk register from per-obligation rows, grouped by regulatory provision (1 LLM call via the `synthesise_register` task method on `BaseLLMClient`). This is where chain state — the per-obligation structured records threaded through Steps 3–4 — gets materialised into rows that conform to SCH-01. The synthesise prompt asks "what's unaddressed?" not "what should the deployer do?" — preserving the Fork A scope claim and producing the `gap_characterisation` field as descriptive (what aspect of the obligation the policy fails to address) rather than prescriptive (what the deployer should do). All schema fields except `gap_characterisation` are mechanically derived from chain state (regulatory_provision from the source chunk metadata; obligation from Step 3 output; match_status from Step 4 output; the three evidence fields from Step 4 retrieval; regulation_chunk_ids and confidence populated post-LLM by chain code).

**Success conditions:**
- Each row in the output register populates all 9 schema fields per SCH-01.
- `gap_characterisation` text is descriptive (what's unaddressed) not prescriptive (what to do) — verifiable by manual inspection of 5 sample rows.
- Provenance fields (`regulation_chunk_ids`, `confidence`) are populated by chain code post-LLM and never appear in the synthesise prompt — verifiable by code review of the prompt template.
- Step 5 can populate every schema field from chain state without re-querying retrieval (chain-state contract verification).

### CHN-06: Verbose / debug mode
> priority: must-have | risk: low
> depends_on: CHN-04, CHN-05

The chain supports a verbose flag that prints intermediate state — retrieval similarities, extracted obligations, silence-threshold checks (`max_sim`, `τ`, decision), per-obligation classifications. This is the build-time observability mechanism (G1 guardrail from D-007 amendment, audited to a one-line scope). It is *not* a structured logging system — print statements via verbose mode plus the cache (which provides reproducibility for LLM calls) is the full observability story for the build. Verbose mode is what makes the silence-detection sanity check (CHN-04 success condition) possible and what supports debugging of the 5 hand-written test queries during build.

**Success conditions:**
- Setting verbose mode produces visible intermediate-state output for: per-sub-question retrieval similarities, the obligations extracted at Step 3, per-obligation `max_sim` and `τ` and the silence decision at Step 4 Phase 1, and per-obligation classifications at Step 4 Phase 2.
- Verbose mode does not change any chain output — only prints additional information.
- A quiet-mode end-to-end run produces no debug output by default.

### CHN-07: End-to-end latency budget on Gemma uncached
> priority: must-have | risk: medium
> depends_on: CHN-05

End-to-end latency target on Gemma uncached: under 90 seconds (revised upward from 60s in session-002 to reflect the 5-step obligation-level chain). This is a working assumption to be confirmed at the week-3 single-model gate; if breached, escalate via FLEX-5 (chain depth collapse) or accept longer non-demo latency rather than treating it as a hard-fail. Cache pre-warming makes demo and repeated-eval latency sub-second regardless of cold-call budget. Risk is medium because Gemma latency on the 5-step chain depends on prompt lengths that are not pre-validated (risk landscape #10).

**Success conditions:**
- On the 5 hand-written test queries, end-to-end uncached latency on Gemma is under 90 seconds (validated at the week-3 single-model gate).
- If the latency budget is breached, FLEX-5 invocation path or non-demo-latency acceptance is invoked rather than a hard-fail.
- Demo-day cached latency on the planned demo queries is sub-second on both backends (cache pre-warming workflow verified).

## Group: Output Schema
> priority: must-have

The 9-field per-obligation row schema that the chain's synthesise step produces and the UI renders. Small but central — read by CHN Step 5 and by UI for rendering, with its own freeze gate before downstream code consumes it. The schema is symmetric across regulation and deployer side: both carry chunk-level provenance for citation traceability. Standalone value of completing the group: a JSON schema that downstream code can validate against, with a clear contract about which fields are LLM-populated and which are populated by chain code post-LLM. FLEX-4 is exercised pre-freeze if at all.

### SCH-01: 9-field per-obligation row schema
> priority: must-have | risk: medium
> depends_on: -

Each row in the residual-risk register represents one atomic obligation. Nine fields, after the session-002 chunk-provenance audit and the review-resolution amendment:

- `regulatory_provision` — citation (e.g., "GDPR Art 22(3)").
- `regulation_chunk_ids` — list of chunk IDs input to obligation extraction for this sub-question. Populated by chain code post-LLM; never appears in prompts. Coarse-grained provenance suitable for audit, not surgical per-obligation attribution. Symmetric with how `policy_evidence` / `extras_evidence` / `guidance_evidence` cite chunks on the deployer side.
- `obligation` — atomic obligation text extracted in Step 3.
- `match_status` — enum: silent / partial / adequate / contradictory.
- `policy_evidence` — citations + snippets from Novara published AI policy (or empty for silent).
- `extras_evidence` — citations from DPIA / Model Card / Transparency Notice / Annual Governance Report / Model Intake Assessment (or empty).
- `guidance_evidence` — citations from ICO operational guidance (or empty).
- `gap_characterisation` — free-text *describing* what aspect of the obligation the policy fails to address (descriptive, not prescriptive). Framed as gap-surfacing language, not remediation suggestion. Renamed in session-002 review-resolution from `residual_obligation` (which was Fork B disguised as Fork A).
- `confidence` — low / medium / high, derived from retrieval similarity only (e.g., min or mean across the cited evidence chunks). LLM self-assessment is not used (avoids overlap with the D-004 LLM-as-judge exclusion).

JSON-schema-constrained, parsed with retry-on-failure (handled by `RoutingClient`'s schema-parse retry-with-feedback policy). Risk is medium because of risk landscape #1 (schema drift on Gemma 2-2B for complex schemas) — mitigated by simple schema, one retry, primary path is Llama 70B during evaluation.

**Success conditions:**
- The schema definition lists all 9 fields with their types and (where relevant) enum values.
- Schema-validation against output produced by both backends passes on all 5 hand-written test queries.
- `gap_characterisation` is descriptive (not prescriptive) on manual inspection — Fork A discipline holds at the schema level.
- `confidence` is derived from retrieval similarity only — verifiable by inspecting the derivation logic (no LLM call to populate this field).
- The schema is frozen before CHN-05 and UI-01 consume it (schema-frozen gate before week 3).

## Group: User Interface
> priority: must-have

The presentation layer the compliance officer interacts with. Streamlit is the primary path (D-005), with Jupyter notebook as the explicit fallback if Streamlit destabilises late in build. The brief does not require Streamlit — Jupyter is brief-acceptable. Standalone value of completing the group: an interactive surface where the user types a query and sees a rendered residual-risk register with sidebar metadata (retrieval confidence, model in use, cache indicator).

### UI-01: Streamlit primary interface
> priority: must-have | risk: medium
> depends_on: CHN-05, SCH-01

Streamlit interface with: query input, register output (rows rendered expandably so column count doesn't crowd the UI), expandable per-corpus retrieval, sidebar showing retrieval confidence, model in use, and cache indicator. Silent rows render with an explanatory marker ("no policy chunk above similarity τ") — operationalising the abstention cross-cutting concern in the UI. *Streamlit complexity caveat:* if week-6 timeline pressure surfaces, default to Jupyter (UI-02) rather than compress demo polish; Jupyter is brief-acceptable. Risk is medium per risk landscape #4 (Streamlit late in build — UI debugging eats week 6+).

**Success conditions:**
- Streamlit runs locally for the demo path on a representative query.
- Register rows render expandably with all 9 schema fields visible per row.
- Sidebar surfaces retrieval confidence, model in use, and cache indicator.
- Silent rows are rendered with an explanatory marker referencing the silence threshold.
- If week-6 timeline pressure surfaces, the project pivots to UI-02 (Jupyter) rather than compresses demo polish.

### UI-02: Jupyter notebook fallback
> priority: should-have | risk: low
> depends_on: CHN-05, SCH-01

Jupyter notebook fallback wrapping the same chain logic in a simpler interface, following the tutorial week-7 `NewsReader.chat()` loop pattern — query in / register out / loop until exit. Same logic as UI-01 but no Streamlit-specific code; rendering is plain Python printing with a tabular formatting helper. The brief does not require Streamlit, so this fallback is brief-acceptable. Should-have rather than must-have because if Streamlit (UI-01) is stable, the Jupyter fallback is not strictly needed for the demo — but it remains part of the safety net per D-005, and it's the expected demo surface if FLEX-5 / D-005 fallback is invoked under week-6 timeline pressure.

**Success conditions:**
- The Jupyter notebook accepts a user query, runs it through the full chain (CHN-01 to CHN-05), and prints a readable register.
- The interaction loop follows the tutorial `NewsReader.chat()` pattern (query in / register out / exit on sentinel).
- Same chain logic — no chain code is duplicated for Jupyter.
