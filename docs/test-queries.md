# Test Queries

> Five hand-written queries in Maya's voice (Head of AI Compliance, Novara). The build-completion gates run against these. They span the shapes the system needs to handle: multi-facet, single strong-match, single likely-partial, ambiguous, and deliberate silence.
>
> **These are scaffolds — read them, then rewrite or replace to your own voice.** The shapes (column headed *targets*) matter; the exact wording is yours. The silence target especially: pick something *you* understand the policy doesn't address, so you can defend the silence finding in viva.
>
> Each entry includes what the system *should* find (regulation side + deployer side) so you can sanity-check the chain output during the build-completion stage 1 gate.

---

## Q1 — Multi-facet (forces decomposition)

> "TalentLens compliance under EU AI Act Annex III §4 — am I covered on Article 13 deployer instructions, Article 14 human oversight, Article 26 logs and worker information, and the related Article 22 GDPR automated-decisions duties? Where are the gaps?"

**Targets:** multi-facet across two regulatory frameworks (AI Act + GDPR), forces CHN-01 to decompose into ≥3 sub-questions.

**Expected sub-questions** (after CHN-01):
- AI Act Article 13 (instructions for use)
- AI Act Article 14 (human oversight)
- AI Act Article 26 (deployer obligations — logs, worker info)
- GDPR Article 22 (automated decisions)

**Expected regulation-side retrieval:** chunks from EU AI Act Articles 13, 14, 26, plus Annex III §4; GDPR Article 22 chunks.

**Expected deployer-side retrieval:** policy § 3.5 (HITL levels) for human oversight; policy § 4.3 (Right to Explanation, Right to Object) for Article 22; DPIA § 5.1 (R-06 mitigation) for human review.

**Expected `match_status` distribution:** mix of `partial` and `silent`. Article 14 → partial (HITL exists but not framed under Article 14). Article 26 logs → silent (policy has model-weight retention but doesn't address Article 26(6) deployer log-retention duty). Article 26(7) worker information → silent. Article 22 → partial (HITL + opt-out exist; "right to contest", "express point of view" absent).

**Why this query is a good test:** verifies the chain handles legitimate multi-facet complexity without collapsing into one sub-question, and that silence detection fires on at least one row (Article 26(6), Article 26(7), or Article 27 if the chain pulls it in adjacent).

---

## Q2 — Single, strong-match expected

> "Does our policy address the red-teaming requirements before deploying a high-risk AI system to production?"

**Targets:** single sub-question, expected adequate match. Verifies the chain produces an `adequate` classification when policy genuinely addresses the obligation.

**Expected sub-questions:** 1 (red-teaming for high-risk AI).

**Expected regulation-side retrieval:** EU AI Act Article 9 (risk management system) and Article 15 (accuracy, robustness, cybersecurity) chunks.

**Expected deployer-side retrieval:** policy § 3.4 (Red-Teaming and Safety Testing) — covers prompt injection, jailbreak, demographic bias, hallucination, PII leakage; mandates external red-teamer for High-Risk AI Features; G2 gate dependency.

**Expected `match_status`:** `adequate`. Maybe one `partial` if the chain extracts a sub-obligation around documentation retention that's not explicitly policy-addressed.

**Why this query is a good test:** sanity-checks that the system can produce `adequate` classifications. If everything comes back `silent` or `partial`, τ is too high or extraction is hallucinating obligations the policy genuinely covers. Calibration anchor.

---

## Q3 — Single, likely partial

> "How do we meet GDPR Article 22 requirements on solely automated decisions affecting candidates — explicit consent, right to obtain human intervention, right to contest the decision, and right to express their point of view?"

**Targets:** single sub-question, expected `partial`/`silent` mix at the obligation level (Article 22(3) decomposes into 4 distinct obligations).

**Expected sub-questions:** 1 (Article 22 + sub-clauses).

**Expected regulation-side retrieval:** GDPR Article 22 (especially 22(3)) chunks; ICO main-guidance § 07-article-22-fairness; ICO audit-framework § 10-human-review.

**Expected deployer-side retrieval:** policy § 3.5 (HITL Level 2 for High-Risk AI); policy § 4.3 (Right to Object to Automated Profiling); DPIA § 5.1 (R-06 mitigation: human review available on request via Customer); transparency notice (if it covers automated-decision rights).

**Expected `match_status` distribution:** `partial` for "right to obtain human intervention" (HITL covers it, but framing isn't Article-22-explicit and Customer is contractually responsible — partial alignment); `silent` for "right to express their point of view" and "right to contest the decision" (neither phrase appears in any deployer doc); `partial` for "explicit consent for solely automated decisions" (policy talks about consent for training data, not for automated decisions specifically).

**Why this query is a good test:** the 4-state classifier should distinguish between `partial` (touched but incompletely) and `silent` (not addressed at all) — Article 22(3)'s sub-clauses are designed to surface this distinction. If everything comes back the same status, FLEX-1 (per-obligation classification) is the escalation path.

---

## Q4 — Ambiguous query

> "Are we doing enough on transparency for candidates assessed by TalentLens?"

**Targets:** ambiguous regulatory framing — "transparency" could mean Article 13/14 GDPR (information at collection), Article 22(1) GDPR (meaningful information about logic of automated decision), AI Act Article 13 (instructions for use to deployers), AI Act Article 50 (transparency obligations to natural persons), or ICO main-guidance § 03-transparency. Tests how the system handles unclear scope.

**Expected sub-questions:** 3–4 (the decompose step should split this rather than answer as one). Likely sub-questions: GDPR Article 13/14 information duties; Article 22 logic-of-decision transparency; AI Act Article 50 transparency to candidates; transparency-notice content adequacy.

**Expected regulation-side retrieval:** GDPR Articles 13, 14, 22; AI Act Article 50; ICO transparency chapters.

**Expected deployer-side retrieval:** transparency notice (NAI-TN-0011); policy § 4.3 (Right to Explanation); policy § 6 (Transparency principle); DPIA § 5.1 (no specific transparency mitigation).

**Expected `match_status` distribution:** mixed. Information-at-collection duties (Articles 13/14) → likely `partial` (transparency notice exists but content adequacy is the question). Logic-of-decision transparency → `partial` (Right to Explanation exists with 90-day post-GA implementation window — vague). AI Act Article 50 → likely `silent` or `partial` depending on transparency-notice content.

**Why this query is a good test:** ambiguous queries are common in real compliance work — Maya often starts vague before sharpening. The system should decompose meaningfully rather than produce a single thin answer. Stresses the decompose prompt's quality.

---

## Q5 — Deliberate silence target

> "Have we performed a Fundamental Rights Impact Assessment under EU AI Act Article 27 for TalentLens as a deployer of an Annex III high-risk system?"

**Targets:** narrow, specific obligation that the deployer-side documents genuinely don't address. Verifies silence detection fires on a legitimate gap.

**Expected sub-questions:** 1 (Article 27 FRIA).

**Expected regulation-side retrieval:** EU AI Act Article 27 chunks; Annex III chunks (for deployer scope context).

**Expected deployer-side retrieval:** policy § 3.3 mentions DPIA at G2 gate; DPIA itself (NAI-DPIA-0023) is GDPR Article 35-compliant; intake assessment template covers risk classification but not FRIA. **Critically: no document mentions "Article 27", "Fundamental Rights Impact Assessment", or "FRIA" anywhere.** Cosine similarity of the obligation embedding against deployer-side chunks should fall below τ.

**Expected `match_status`:** `silent` deterministically (Phase 1, no LLM call) on the FRIA obligation. The obligation is sharply distinct from the GDPR Article 35 DPIA that the deployer side does carry; even though both are "impact assessments", the sentence-transformer should distinguish them — but if τ is too low, this could leak as `partial`. **This query is the canary for silence-detection calibration at the retrieval-config freeze gate.**

**Adjacent contradiction (worth noting in viva):** policy § 5.4 claims current portfolio is "Limited-Risk", but TalentLens (CV screening) is clearly EU AI Act Annex III §4 high-risk. If the chain extracts an obligation around correct risk classification, the deployer side may produce `contradictory` rather than silent. Either outcome is a valid finding.

**Why this query is a good test:** it has a clear, defensible expected outcome (silent — and the marker can verify by searching the policy for "FRIA" or "Article 27" themselves). It's also a substantively important gap in real compliance terms, not a contrived test case. Best query for the demo's "look, the system catches this" moment.

---

## How to use this set during the build

1. **Retrieval-config freeze gate:** Q1, Q2, Q3 are the recall-test queries (do regulation chunks for the named articles appear in top-5?). Q4 tests retrieval on ambiguous framing. Q5 tests retrieval at the τ boundary.

2. **Extraction-quality gate (after CHN-03):** Q1 and Q3 are best for the 30-sample obligation extraction check — they produce many obligations across multiple sub-questions. Q5 is a single-sub-question check.

3. **Build-completion stage 1:** all 5 queries run end-to-end on both backends. Inspect the registers for: (a) JSON parses cleanly, (b) all `match_status` values fall in the enum, (c) every non-silent row has citations, (d) Q5 shows at least one `silent` row with `max_sim` and `τ` logged in verbose mode, (e) Q2 shows at least one `adequate` row.

4. **Demo:** Q1 or Q5 are best for the demo. Q5 is more dramatic (silence-detection moment); Q1 shows the system handling legitimate multi-facet complexity. Pick based on whether the demo narrative is "look how the system finds gaps" (Q5) or "look how the system structures complex compliance questions" (Q1).
