# Decisions

> Pre-build decisions, made for you with full reasoning. Each entry is viva-ready text — read it aloud, you can defend it.
>
> **You own these.** If you find evidence during build that a call was wrong, override it and add a note to the decisions log at the bottom. The "considered alternative" line tells the marker you knew the trade-off; the "why this" line tells them you chose deliberately.

---

## 1. How `confidence` is computed for each row

**Decided:** Aggregate cosine similarity over the cited evidence chunks using **`min`** (the weakest cited chunk sets confidence). Provisional bins: `min ≥ 0.55 → high`, `min ≥ 0.45 → medium`, otherwise `low`. Re-tune the bin boundaries at the retrieval-config freeze gate using the τ histogram data.

**Why `min` not `mean`:** This system surfaces gaps for compliance review. Confidence should be honest about the *weakest* cited evidence, because a borderline citation in the chain is what compliance officers care about. Mean smooths over weak citations and hides the failure mode you're trying to expose. `min` reflects "the worst chunk we cited" — the right semantic for Fork A scope.

**Why provisional bins:** Cosine values on `multi-qa-MiniLM-L6-cos-v1` typically run 0.3–0.7 for relevant matches on prose. 0.55 / 0.45 splits the typical "good match" / "borderline" / "weak" zones. The actual distribution on legal text is what the freeze-gate spot-check measures — the bins get tuned then.

---

## 2. `confidence` value for silent rows

**Decided:** **`high`**. Reaffirmed 2026-05-04 after user concern about response-quality pollution.

**Why:** Silent classification is *deterministic* — `max_sim < τ` is a mechanical comparison, not an LLM judgment. The system is highly confident *that the policy is silent on this obligation*. Calling it `low` would imply uncertainty about the silence verdict, which is the opposite of what's true.

**Why this doesn't pollute response quality (reaffirmed 2026-05-04):** The `confidence` field is **post-hoc metadata** populated by chain code after CHN-05 — it never enters any prompt, doesn't influence retrieval, and doesn't change classification. Setting silent rows to `confidence: high` is a labelling decision, not a quality lever. Response quality is governed by retrieval recall (RET), obligation extraction (CHN-03), and the classifier (CHN-04 Phase 2); none of those touch this field. Two distinct concerns can be conflated here: (a) "are too many silent rows being flagged?" is a τ-tuning question, addressed by decision #4 at the retrieval-config freeze gate; (b) "do high-confidence silent rows look indistinguishable from high-confidence adequate rows in the UI?" is a presentation question, addressed by SCH-01 and UI-01's mandated visible marker on silent rows ("no policy chunk above similarity τ"). Neither concern is a quality risk on the chain output itself.

**Considered:** Adding a fourth value (`n/a` or empty) for silent rows; reversing to `silent → low` to signal structural distinction.

**Why not:** `n/a` adds a special case to a clean three-value enum. `silent → low` is misleading — implies LLM uncertainty when none exists. If the Streamlit prototype reveals user confusion in week 5, the cleanest fix is FLEX-4: extend the enum to `low / medium / high / structural` (~30 min schema tweak + UI renderer update), not retreat from the structural-honesty position.

**Watch trigger to revisit (2026-05-04):** Streamlit prototype review at week 5 — observe whether high-confidence silent rows feel indistinguishable from high-confidence adequate rows on a multi-sub-question query. Eval-phase demo rehearsal — if marker preview / domain-expert review surfaces confusion, FLEX-4 to add a `structural` enum value is the documented escalation.

---

## 3. Sub-question decomposition cap (CHN-01)

**Decided:** Cap at **4** sub-questions per query. Enforce in the decompose prompt; validate in chain code post-LLM and truncate to 4 if the model produces more.

**Why 4:** Genuine compliance queries can legitimately span 4 facets (e.g., "Article 22 automated decisions + Article 13/14 transparency + DPIA under Article 35 + Annex III high-risk classification"). Capping at 3 would force premature aggregation in the decompose step and lose register granularity.

**Considered:** Cap at 3 (matches the spec's typical-case working assumption); cap at 5+ (more headroom).

**Why not 3:** Suppresses legitimately multi-faceted queries. **Why not 5+:** Each extra sub-question adds ~2 LLM calls (extract + classify); 5 sub-questions = ~12 calls per query, which strains Groq's free-tier rate budget without a recall improvement.

---

## 4. τ histogram rule for the retrieval-config freeze gate spot-check

**Decided:** At the freeze gate, compute `max_sim` for ~30 sampled obligations against each deployer-side corpus (policy / extras / guidance). Take the **median** across all (obligation × corpus) max-sim values.

- If median ≥ 0.35 → raise τ to `median + 0.05`
- If median < 0.35 → keep τ = 0.35 (the spec's conservative default is doing its job)

**Why median + 0.05:** Median sits in the bulk of the distribution; +0.05 places τ above the bulk so most obligations don't trip silence by default. The 0.05 is a small buffer, not a calibration claim. Defendable as a sanity-floor adjustment, not a tuning exercise (the spec is explicit that build-time τ is *not* calibration; eval-phase calibration comes later).

**Considered:** Use mean instead of median; pick τ by eyeballing the histogram at the gate.

**Why not mean:** Sensitive to outliers — one Article that perfectly matches a policy clause skews the mean upward and would push τ too high. **Why not eyeball:** Under build pressure at the gate, having the rule pre-committed is faster and more defensible than re-deriving it.

---

## 5. Token-budget guard for the batched classifier (CHN-04)

**Decided:** Estimate prompt token count before the call (`len(prompt_string) // 3.5` for English). Fall through to per-obligation classification (FLEX-1) for *just this sub-question* if the estimate exceeds:

- **5,000 tokens** on Gemma 2-2B-it (8K context, ~3K reserved for response — context window is the binding constraint)
- **15,000 tokens** on Llama 70B via Groq — **placeholder, to be tuned at the retrieval-config freeze gate** (see watch trigger below)

Log the fall-through in verbose mode (CHN-06) so it's visible when it fires.

**Why these numbers (revised 2026-05-04):** Gemma's 5K is well-grounded — context window 8K minus ~3K reserved for response. The Llama number is harder to pin down before we see real prompt sizes:

- Llama 3.3 70B has a **128K context window** — context is *not* the binding constraint.
- **The binding constraint is Groq's free-tier rate limit:** TPM 12K, TPD 100K, RPM 30, RPD 1K (per `console.groq.com/docs/rate-limits`).
- A single prompt above ~10–11K tokens consumes the entire per-minute TPM budget, so the next call gets throttled.
- TPD 100K caps fully-uncached chain queries at ~10 per day before throttling — cache pre-warming (LLM-06) is essential.

The 15K placeholder is fine because failure is graceful: if the guard lets a 15K prompt through and Groq rate-limits it, `RoutingClient` catches the error and falls back to Gemma (LLM-05's hardcoded policy). Worst case is one slow call, not a corrupted register.

**Watch trigger (2026-05-04):** instrument CHN-04 to log estimated prompt size in verbose mode. At the retrieval-config freeze gate (end of week 2), tabulate prompt-size distribution across the 5 hand-written queries; tighten or loosen the Llama guard based on observation. Build-time observation tracked as BO-007 in the private build plan.

**Considered:** No guard, always batch and hope; always per-obligation, never batch; commit to a tight 9K Llama guard now.

**Why not no-guard:** Silent truncation corrupts classifications without a visible error — exactly the failure mode that destroys trust in the demo. **Why not always-per-obligation:** ~3× more LLM calls per query; rate limits become the bottleneck and uncached query latency triples. **Why not commit-9K-now:** premature without empirical prompt sizes; 15K-with-graceful-fallback is the same outcome with less re-tuning friction.

---

## 6. Retrieval top-k values

**Decided:** **`top_k = 5`** everywhere — for regulation retrieval in CHN-02 (per sub-question) and for each deployer-side corpus in CHN-04 phase 2 (policy, extras, guidance separately).

For silence detection in CHN-04 phase 1, use the maximum cosine similarity from the top-5 results per deployer-side corpus, then take the overall max across the three corpora.

**Why a single value everywhere:** One number to remember, one place to tune, and 5 is the right size for both jobs:
- For obligation extraction (CHN-03): 5 regulation chunks per sub-question gives the LLM enough context to extract ~5 atomic obligations without flooding the prompt.
- For evidence retrieval (CHN-04 phase 2): 5 chunks per deployer-side corpus = up to 15 candidate evidence chunks per obligation, which the classifier prompt can comfortably handle.
- For silence detection (CHN-04 phase 1): max over top-5 per corpus is more noise-robust than top-1 and stays cheap (no extra retrieval — same call returns the scores).

**Considered:** Different `top_k` per step (e.g., top-3 for silence detection, top-7 for regulation retrieval).

**Why not:** Adds tuning surface without a clear win at this scale. Single `top_k` keeps the retrieval interface simple and is cheaper to defend in viva.

---

## 7. Demo persona

**Decided:** **Maya, Head of AI Compliance** — used as a **drafting voice for the 5 hand-written test queries only**. Not named in the UI, not named in the report, not part of the demo narrative.

**Why:** A single coherent voice for the queries (direct, regulatory-shorthand-comfortable: "Art 22", "Annex III §4") makes them sound like real compliance prose rather than a heterogeneous test set. But the system itself doesn't need a named persona on screen — markers reward the substance of the gap-surfacing claim, not a UX framing. Keeping Maya backstage preserves the query-quality benefit while avoiding extra surface area to defend in viva.

**Override note (2026-05-04):** Daria's earlier instruction was to drop the persona entirely. After review of the test queries (calibrated to the gates and grounded in real policy gaps), the option-3 compromise was adopted: keep Maya as drafting voice only; never expose her in user-facing artefacts. The drafted queries keep their existing voice.

---

## 8. Product name

**Decided:** **TalentLens**, confirmed.

**Why:** Already used throughout the corpus extras (DPIA, Model Card, Transparency Notice, Annual Governance Report, Model Intake Assessment) and the strategic spec. Renaming now means rewriting all five extras for no benefit.

---

## 9. Streamlit theme

**Decided:** Single accent colour `#1E40AF` (professional blue, fits the Novara-AI fictive brand) on white background. Default Streamlit fonts. No custom CSS.

**Why:** Cosmetic — the markers reward the *content* of the demo, not visual polish. Single accent + defaults is 5 minutes of `.streamlit/config.toml` and looks coherent. Custom CSS is a time sink that returns nothing on the rubric.

Apply once UI-01 functional behaviour is stable. If demo deadline pressure surfaces, ship with full Streamlit defaults — also acceptable.

---

## 10. Build-phase budget commitment

**Default assumption:** ~12–15 hours/week of focused build time across the build phase, per spec.

**What you need to do:** Sketch your real availability against the build phase (term commitments, exam periods, anything that pulls focus). If any stretch falls materially below the assumed budget, flag it in the decisions log — those stretches are candidates for FLEX-5 invocation (chain depth collapse) rather than over-commitment.

**Why this matters:** This is the one decision only you can make — your real availability. The architecture is sized assuming the spec's budget; if reality is tighter, FLEX-5 is the planned response, not a panic move. Logging the gap honestly also gives you a defendable narrative in the report's limitations section: "the build was sized assuming X hours; actual was Y; here's how I adapted."

---

## Explicitly deferred — do NOT decide now

These exist on the build timeline but are deliberately not decided yet. Picking them prematurely defeats their purpose.

| Decision | When to decide | Why deferred |
|---|---|---|
| Embedding model (FLEX-3) | At the retrieval-config freeze gate | The decision is informed by retrieval recall on the actual corpus + queries; deciding now is a guess against unknown distribution |
| Sentence aggregation mode (FLEX-3 intermediate) | At the retrieval-config freeze gate, only if RET-01 underperforms | Same reason — needs measurement, not a guess |
| `severity` schema field (FLEX-4 candidate) | Eval-phase mid-point | Trigger requires gold-set evidence that prioritisation is load-bearing for the demo narrative |
| `sub_question` schema field (FLEX-4 candidate) | After UI-01 first runs end-to-end against multi-sub-question queries | Trigger requires UI evidence that the flat register feels disorienting on multi-sub-question queries |

If pressure mounts to decide one of these early, that's a signal to revisit the trigger — not to skip it. Let your assistant make the case in writing first.

---

## Decisions log (build-time)

Decisions made *during* the build go here, newest first. Format:

```
### [Title] — [triggering capability or gate]
**Decided:** [chosen value]
**Reason:** [one sentence — what tipped the call]
**Updates `build-notes.md`?** [yes/no]
```

### Skip AI Act recitals during ING-02 chunking — pre-build review (2026-05-04)
**Decided:** ING-02 starts chunking the EU AI Act `.txt` from line 3915 (Article 1) onward. Recitals 1–180 (lines ~60–3914) are excluded from the chunked content.
**Reason:** Recitals are interpretive paragraphs explaining *why* each provision exists; they're not directly enforceable obligations. Including them risks CHN-03 extracting pseudo-obligations from explanatory text and corrupting downstream classification — exactly the high-risk failure mode noted in the spec for CHN-03. The compliance gap analysis system's distinctive claim is that obligations are extracted from operative provisions and matched against deployer policy. Recitals carry no obligations; including them adds noise without clear retrieval benefit. Reasoning recorded in full at `docs/ai-act-extraction-notes.md` § "Recitals — chunk or skip?".
**Considered:** (a) chunk separately with a `recital_id` metadata flag for use as supporting context; (b) chunk inline with articles, no flag.
**Why not (a):** adds chunk count and asks the synthesise prompt to handle a new modality (interpretation note vs obligation evidence) without a strong reason it'll improve gap-surfacing quality. **Why not (b):** simplest but most likely to corrupt CHN-03 (extraction prompt sees recital text and may treat it as an obligation).
**Trigger to revisit:** if retrieval recall on broad / context-heavy queries is poor at the retrieval-config freeze gate, option (a) is the FLEX path — chunk recitals separately with a metadata flag, never feed to CHN-03 extraction, optionally surface in CHN-05 synthesise as interpretive context.
**Updates `build-notes.md`?** No (build-notes does not specify chunking-level implementation choices).

### Decision #5 token guard — Llama number revised to placeholder + watch (2026-05-04)
**Decided:** Keep 15K Llama guard as a placeholder; tune at the retrieval-config freeze gate (end of week 2) using empirical prompt-size logging from the 5 hand-written queries. Gemma 5K stays unchanged.
**Reason:** Verified Groq's actual free-tier limits (TPM 12K, TPD 100K, RPM 30, RPD 1K, context 128K). Hard-committing the Llama number before observing real prompt sizes is premature; failure is graceful (rate-limit → Gemma fallback via RoutingClient).
**Updates `build-notes.md`?** No (build-notes does not list specific guard values).

### Decision #2 silent-row confidence — rationale extended for response-quality concern (2026-05-04)
**Decided:** Keep `confidence: high` for silent rows. Watch trigger added: revisit at week-5 Streamlit prototype review or eval-phase demo rehearsal.
**Reason:** User concern that `confidence: high` could pollute response quality. Verified that the field is post-hoc metadata (never enters prompts, doesn't influence retrieval/classification) — it cannot affect chain quality. UX disambiguation is handled by the spec-mandated UI marker on silent rows. If user confusion appears at the prototype gate, FLEX-4 to add a `structural` enum value is the cleanest escalation.
**Updates `build-notes.md`?** No.

### Maya persona scope narrowed to drafting voice only — pre-build review (2026-05-04)
**Decided:** Override decision #7 to scope Maya as a drafting persona for test queries; remove her from any user-facing artefact (UI, report, demo).
**Reason:** Reconciles Daria's earlier "no demo persona" instruction with Bogdan's pre-built queries that lean on a single coherent voice — keeps the query quality, drops the on-screen exposure.
**Updates `build-notes.md`?** No (build-notes never named a persona).
