# Intentional Gaps Inventory

> **What this is.** A catalogued inventory of gaps engineered into the synthetic deployer corpus (Novara AI v3.1 policy + 5 supporting documents) when measured against the regulatory and operational guidance corpora (EU AI Act, UK/EU GDPR, ICO AI guidance suite). The system is *designed* to surface these; this document lets the build verify it actually does.
>
> **Why this exists.** Three uses: (1) test-query design — choose demo questions that reliably trigger each gap; (2) build-time correctness check — at the build-completion gate, confirm the residual register surfaces these gaps with the expected `match_status`; (3) viva defence — a marker can independently verify any silence finding in this doc by grep, without taking the system's claim on trust.
>
> **How it was built.** Manual cross-reference of the Novara policy text + 5 deployer-extras against the regulation and ICO guidance buckets, with grep-verified silence claims. Each gap entry below records: regulatory source · what's required · what the deployer side covers (if anything) · verification method · demo utility · suggested query.
>
> **Maintenance.** Update when (a) the deployer corpus is amended (per `v2_corpus_specification.md` § 7, this means a new `corpus-vN/` snapshot, not in-place edit) or (b) a build-time observation reveals a gap not catalogued here. Companion to `docs/test-queries.md` — five of the gaps below are the explicit targets of the five build-time test queries.

---

## Verification methodology

Each silence claim was tested with a recursive grep across `corpus/deployer/` and `corpus/deployer-extras/` — case-insensitive, regex-aware, including obvious phrasings and abbreviations. Examples below are reproducible:

```bash
# G1 — FRIA / Article 27
grep -rin -E "FRIA|Article 27|Fundamental Rights Impact Assessment|fundamental.rights.impact" corpus/deployer/ corpus/deployer-extras/

# Sanity (the same patterns *do* appear in the regulation):
grep -in -c "Article 27|Fundamental Rights Impact" corpus/regulation/eu-ai-act-2024-1689.txt
```

When a phrase has no hits in deployer-side and ≥1 hit in regulation-side, the gap is grep-verified silent.

For partials and contradictions, verification is a manual read pointer (section + line range) rather than grep — the policy *touches* the obligation and the call is whether coverage is adequate.

---

## Gap classification

Five labels are used:

- **🔴 SILENT (G)** — the obligation is not addressed anywhere on the deployer side. The system should classify the row `silent` deterministically (cosine similarity below τ).
- **🟠 CONTRADICTORY (C)** — the deployer side asserts something inconsistent with the regulation. The system should classify the row `contradictory` (LLM judgment).
- **🟡 PARTIAL (P)** — the deployer side touches the obligation but coverage is incomplete or under-specified. The system should classify the row `partial`.
- **🟢 ADEQUATE (A)** — included only as calibration anchors so the system has examples it should NOT flag as gaps. The system should classify the row `adequate`.
- **⚪ N/A** — the obligation is not applicable to Novara/TalentLens (e.g., provider-side obligations when Novara is the provider but the obligation falls on a different actor).

---

## Silences — grep-verified zero hits across deployer corpus

### G1 — EU AI Act Article 27: Fundamental Rights Impact Assessment (FRIA) ⭐⭐⭐⭐⭐

- **Regulatory source:** EU AI Act Art 27 — deployers of high-risk AI systems listed in Annex III must conduct an FRIA prior to first use, covering processes affected, period of use, categories of natural persons affected, specific risks of harm, human oversight measures, and arrangements for handling adverse impacts.
- **What's required:** A documented FRIA, distinct from a GDPR DPIA, with the listed elements; supplied to the relevant national authority on request.
- **What the deployer side covers:** Nothing. The Novara policy mentions DPIA at Gate G2 (§3.3), and a `novara-talentlens-dpia.md` exists in deployer-extras — but the DPIA is GDPR Art 35-compliant only. No mention of FRIA or Art 27.
- **Verification:** `grep -rin -E "FRIA|Article 27|Fundamental Rights Impact" corpus/deployer/ corpus/deployer-extras/` → **0 hits**. Sanity: same pattern in `corpus/regulation/eu-ai-act-2024-1689.txt` → 10 hits.
- **Demo utility:** ⭐⭐⭐⭐⭐ — the canary silence target. Marker can verify by grep in 5 seconds. Substantively important: FRIA is a deployer-specific obligation introduced in 2024 and is the load-bearing example of why a CV-screening tool's compliance posture isn't covered by GDPR alone.
- **Targeted by:** `docs/test-queries.md` Q5.
- **Suggested demo query:** *"Have we performed a Fundamental Rights Impact Assessment under EU AI Act Article 27 for TalentLens as a deployer of an Annex III high-risk system?"*

### G2 — EU AI Act Article 26(7): Worker information obligation ⭐⭐⭐⭐

- **Regulatory source:** EU AI Act Art 26(7) — before putting into service or use a high-risk AI system at the workplace, deployers who are employers must inform workers' representatives and the affected workers that they will be subject to the use of the high-risk AI system, in accordance with applicable EU and national law on workers' information.
- **What's required:** Documented worker-information process; notification to workers' representatives prior to deployment; affected workers individually informed.
- **What the deployer side covers:** Nothing. The policy describes internal training (§7) and HITL (§3.5), but never the deployer-as-employer obligation to inform workers/candidates that they are being assessed by AI. The transparency notice is to candidates (data subjects), not workers in the Art 26(7) sense.
- **Verification:** `grep -rin -E "Article 26|worker.*information|inform.*worker" corpus/deployer/ corpus/deployer-extras/` → 0 hits.
- **Demo utility:** ⭐⭐⭐⭐ — high stakes: deployer-as-employer duty under AI Act, often missed in compliance reviews. Less famous than Art 27 but a real gap.
- **Targeted by:** Q1 (multi-facet).
- **Suggested demo query:** *"Does our policy meet the EU AI Act Article 26(7) obligation to inform workers' representatives and affected workers when high-risk AI is used in employment decisions?"*

### G3 — EU AI Act Article 26(6): Deployer log retention ⭐⭐⭐⭐

- **Regulatory source:** EU AI Act Art 26(6) — deployers of high-risk AI systems shall keep the logs automatically generated by the high-risk AI system for a period appropriate to the intended purpose, of at least 6 months (subject to applicable EU/national law).
- **What's required:** Automatic logs from the AI system retained ≥6 months by the deployer.
- **What the deployer side covers:** §4.4 has retention for *model weights* (5 years post-deployment), *inference logs containing PII* (30 days), *inference logs without PII* (12 months extendable to 24). Adjacent but framed for GDPR purposes, not Art 26(6) deployer-log retention. No reference to Art 26 at all.
- **Verification:** `grep -rin -E "Article 26|deployer.*log retention|log retention.*deployer|automatically generated logs"` → 0 deployer-side hits.
- **Demo utility:** ⭐⭐⭐ — partial overlap with §4.4 retention table makes this a *good* test of granularity: the system should distinguish "we retain logs" (GDPR-framed) from "we retain logs for the Art 26(6) duty" (AI-Act-deployer-framed). Mid-difficulty silence.
- **Targeted by:** Q1.
- **Suggested demo query:** *"How do we comply with EU AI Act Article 26(6) on retaining the high-risk system's automatically-generated logs for at least six months?"*

### G4 — GDPR Article 22(3): "Right to express their point of view" ⭐⭐⭐⭐

- **Regulatory source:** GDPR Art 22(3) — when the decision is based solely on automated processing (including profiling), the data subject has the right to obtain human intervention, **to express his or her point of view**, and to contest the decision.
- **What's required:** A documented mechanism for the candidate to express their point of view about the AI's decision before/after a determination is made.
- **What the deployer side covers:** Nothing. The policy has Right to Explanation (§4.3, 90-day post-GA), Right to Object to Automated Profiling (§4.3), Right to Erasure, Right to Rectification — but never the "express point of view" sub-clause of Art 22(3).
- **Verification:** `grep -rin -E "right to express|point of view"` → 0 hits anywhere on deployer side.
- **Demo utility:** ⭐⭐⭐⭐ — fine-grained silence inside an obligation that the policy *almost* covers. Tests whether the system can distinguish sub-clauses within Art 22(3) rather than blurring "Article 22 is partially addressed."
- **Targeted by:** Q3 (Article 22 sub-clauses).
- **Suggested demo query:** *"Does the policy give candidates a right to express their point of view about the AI's decision under GDPR Article 22(3)?"*

### G5 — GDPR Article 22(3): "Right to contest the decision" ⭐⭐⭐⭐

- **Regulatory source:** GDPR Art 22(3) — third sub-clause of the same provision as G4: data subject has the right to *contest the decision*.
- **What's required:** A documented contest/appeal mechanism distinct from explanation, opt-out, or human intervention.
- **What the deployer side covers:** Nothing. Same situation as G4. The transparency notice may give the candidate explanation rights, but no formal contest pathway.
- **Verification:** `grep -rin -E "right to contest|contest the decision"` → 0 hits.
- **Demo utility:** ⭐⭐⭐⭐ — paired with G4 in Q3. Two distinct sub-obligations within Art 22(3) both silent → strong evidence the system distinguishes obligations at sub-clause granularity.
- **Targeted by:** Q3.
- **Suggested demo query:** *"What process does TalentLens give candidates to contest an automated rejection under GDPR Article 22(3)?"*

### G6 — GDPR Article 22(3): "Right to obtain human intervention" (data-subject-rights framing) ⭐⭐⭐

- **Regulatory source:** GDPR Art 22(3) — first sub-clause: right to obtain human intervention on the part of the controller.
- **What's required:** A data-subject-facing mechanism to *request* human intervention on a specific decision affecting them.
- **What the deployer side covers:** "Human intervention" appears once in the policy (§6 Responsible AI principles, line 342), framed as a deployer principle ("Novara AI will not deploy AI Systems designed to operate without any possibility of human intervention or override"). This is about Novara's internal deployment posture, *not* the data subject's right to request intervention. HITL Levels 1/2/3 (§3.5) are internal review processes, not subject-rights mechanisms.
- **Verification:** `grep -rin -E "human intervention"` → 1 hit, but reading line 342 in context confirms the framing is internal not subject-facing.
- **Demo utility:** ⭐⭐⭐ — borderline: the system might classify this `partial` (because "human intervention" *appears* and HITL exists) rather than `silent`. Tests cross-contamination resistance: can the chain distinguish phrasing from semantics?
- **Targeted by:** Q3.
- **Risk:** Q3 may classify G6 as `partial` rather than `silent`. Both are defensible; if the chain consistently picks `partial`, that's a finding worth recording, not a defect.

### G7 — GDPR Article 22(2)(c): Explicit consent for solely automated decisions ⭐⭐⭐

- **Regulatory source:** GDPR Art 22(2)(c) — Art 22(1) prohibition does not apply if the decision is based on the data subject's *explicit consent* (one of three exceptions).
- **What's required:** Documented basis for processing solely-automated decisions: either contract necessity, legal authorisation, or explicit consent specifically for the automated decision.
- **What the deployer side covers:** "Explicit consent" appears in §4.1 — but only as a legal basis for *training data* and *sharing inference outputs with third parties*. Never as a basis for the solely-automated decision itself under Art 22(2)(c).
- **Verification:** `grep -rin -E "explicit consent.*automated|consent.*solely automated|Article 22.*consent"` → 0 hits in deployer side. "Explicit consent" hits in §4.1 (training data context only).
- **Demo utility:** ⭐⭐⭐ — tests semantic granularity: same phrase ("explicit consent") used with different referents (training data vs automated decision); the chain should distinguish.
- **Targeted by:** Q3 / Q4.
- **Suggested demo query:** *"What's our legal basis under GDPR Article 22(2) for using TalentLens to make solely automated decisions on candidates?"*

---

## Contradictions

### C1 — "Limited-Risk" classification claim ⭐⭐⭐⭐⭐

- **Regulatory source:** EU AI Act Annex III §4 (employment, workers management, access to self-employment), §5 (access to and enjoyment of essential services), Annex III as a whole. Systems falling within Annex III are *high-risk* by definition.
- **What's required:** Correct self-classification under the Annex III framework, with all corresponding deployer obligations applying.
- **What the deployer side claims (the contradiction):**
  - Policy §5.4 (line 311): *"EU AI Act obligations applicable to Novara AI's risk classification (confirmed by Legal as **'Limited-Risk'** for current product portfolio, subject to annual re-assessment)"*.
  - `novara-2025-ai-governance-report.md` line 29: *"EU AI Act risk classification: Limited-Risk for the current product portfolio (subject to annual re-assessment)"*.
  - Same report lines 43–49: every product in the portfolio table — TalentLens (HR), NovaraScore-FS (credit), NovaraDx (healthcare), LegalLens (legal), ContentGuard (content moderation), RetailMatch (customer segmentation), ServiceFlow (workflow automation) — is labelled "Limited-Risk".
- **Why it contradicts:**
  - **TalentLens:** CV screening sits squarely in Annex III §4(a) ("recruitment or selection of natural persons, in particular to place targeted job advertisements, to analyse and filter job applications, and to evaluate candidates").
  - **NovaraScore-FS:** Credit decisioning sits in Annex III §5(b) ("creditworthiness of natural persons or to establish their credit score").
  - **NovaraDx:** Clinical decision support is high-risk by Annex III §1 if used as safety component of a medical device, otherwise still elevated risk.
  - The "Limited-Risk" label is structurally wrong for at least three products in the portfolio.
- **Verification:** Read directly — `corpus/deployer/novara-ai-policy-v3.1.txt` line 311, `corpus/deployer-extras/novara-2025-ai-governance-report.md` lines 29 and 43–49.
- **Demo utility:** ⭐⭐⭐⭐⭐ — strongest substantive finding in the corpus. Marker-defendable: Annex III §4 wording is explicit about CV screening. Pairs with G1 (FRIA) for a strong demo arc — "the policy claims TalentLens is Limited-Risk, *and* it doesn't have a FRIA, *and* both errors are because they self-classified incorrectly".
- **Targeted by:** Q5 surfaces this as adjacent to FRIA silence.
- **Suggested demo query:** *"How does TalentLens fit into the EU AI Act risk classification — is the policy's 'Limited-Risk' assessment correct given Annex III §4?"*

---

## Partials — manual review pointers (not grep-verified)

These are nuanced calls. The deployer side touches the obligation; the question is whether coverage is complete or under-specified. Daria's read of the policy will refine these.

### P1 — EU AI Act Art 14 (Human oversight) — partial

- **What's required:** Human oversight measures including (a) understand capabilities/limitations, (b) monitor operation, (c) interpret outputs, (d) override or disregard outputs, (e) human override switch (Art 14(4)).
- **What the policy has:** §3.5 HITL Levels 1/2/3 with detailed criteria for each level; mandatory Level 1 for healthcare/legal/financial; Level 2 for other High-Risk Features.
- **Why partial:** HITL framework is solid but never explicitly maps to Art 14(4) sub-criteria. Art 14(4)(c) "interpret outputs" especially — does a 5%-sample reviewer "interpret" outputs in the Art 14 sense? Unclear.
- **Demo utility:** ⭐⭐⭐ — adjacent to Q1 multi-facet.

### P2 — EU AI Act Art 50 (Transparency to natural persons) — partial

- **What's required:** Natural persons exposed to specific AI systems (chatbots, emotion-recognition, biometric categorisation, synthetic content) informed in clear and distinguishable manner.
- **What the deployer side has:** §6 Transparency principle ("Users must be informed when interacting with AI-generated content or AI-influenced decisions"); a transparency notice extra exists.
- **Why partial:** The §6 principle covers "AI-influenced decisions" (good for TalentLens) but not the Art 50 specific cases (emotion recognition, biometric categorisation). The transparency notice content adequacy is the open question.
- **Demo utility:** ⭐⭐⭐ — Q4 ambiguous-query test target.

### P3 — GDPR Art 22(3) "meaningful information about logic" — partial bordering on inadequate

- **What's required:** When a decision is based solely on automated processing, the controller provides meaningful information about the logic involved.
- **What the policy has:** §4.3 "Right to Explanation: Product teams must implement an explanation endpoint **within 90 days of GA launch**".
- **Why partial:** A 90-day post-GA implementation window means new High-Risk launches operate without an explanation endpoint for their first 3 months — non-compliant with Art 22(3) for that window. *Borderline contradictory.* If the chain catches this nuance, it's a strong finding.
- **Demo utility:** ⭐⭐⭐⭐ — subtle but provable. Worth highlighting in the demo: "the policy *appears* to address explanation, but the implementation timeline puts the deployer in non-compliance for 90 days".

### P4 — GDPR Art 9 (Special category data) — partial

- **What's required:** Lawful basis for processing special-category data (Art 9(2)) — including racial/ethnic origin, religious beliefs, health, etc. CV processing routinely sees these (photo, name → ethnic origin; volunteer activities → religious affiliation; gaps in employment → health).
- **What the policy has:** §3.4 mandates bias audits across "race, gender, age, disability, religion, national origin, sexual orientation"; §3.2 demographic skew documentation.
- **Why partial:** Bias audits are downstream mitigation; what's missing is the upstream Art 9 lawful-basis assessment for *processing* special-category data in CVs in the first place. The DPIA may or may not cover this — read the DPIA to confirm.
- **Demo utility:** ⭐⭐⭐ — useful in viva to show the system catches GDPR layering (Art 9 ≠ Art 5 fairness).

### P5 — GDPR Art 28 (Processor obligations) — partial

- **What's required:** Controller-processor relationships documented per Art 28(3): subject matter, duration, nature, purpose; processor obligations on confidentiality, security, sub-processors, data subject rights assistance, etc.
- **What the policy has:** §3.2 mentions "signed Data Processing Addendum that includes an AI Training Exhibit" for customer-data opt-in; §3.5 places HITL responsibility partially on the customer.
- **Why partial:** Customer-side DPAs are referenced but the policy doesn't explicitly establish Novara's controller/processor status formally; the Art 28(3)(a–h) list isn't enumerated. The *contract* (DPA) presumably covers this, but contracts aren't in the corpus.
- **Demo utility:** ⭐⭐⭐ — hits the audit-framework chapter on contracts (`ico-audit-framework/04-contracts-and-third-parties.txt`).

### P6 — EU AI Act Art 9 (Risk Management System) — partial

- **What's required:** Continuous, iterative RMS process planned and run throughout the entire lifecycle of the high-risk AI system, regularly reviewed and updated.
- **What the policy has:** §5.2 AI Risk Register (Jira project AI-RISK) with risk categories, mitigation owners, review cadences (bi-weekly to quarterly).
- **Why partial:** Good operational coverage of risk identification and review. Missing: explicit Art 9-style RMS *lifecycle* framing — the iterative-throughout-lifecycle commitment, the periodic-update obligation, the documentation requirements.
- **Demo utility:** ⭐⭐ — technical nuance, lower demo utility than the silences above.

### P7 — EU AI Act Art 13 (Instructions for use) — partial / N/A overlap

- **What's required:** Provider of a high-risk AI system supplies instructions for use to the deployer.
- **Note:** This is a *provider-side* obligation. Novara is provider of TalentLens *and* deployer of TalentLens (sells to customers who deploy). The policy's customer-facing documentation (Model Card extra) is partially Art 13-shaped but doesn't explicitly cite Art 13.
- **Demo utility:** ⭐⭐ — gets into provider/deployer role complexity. Skip for demo unless the audience is technically deep.

---

## Adequates — calibration anchors (system should NOT flag these)

These are deliberately strong matches. If the system classifies any of these `silent` or `partial`, τ may be too high or extraction is hallucinating obligations.

### A1 — EU AI Act Art 15 (Accuracy, robustness, cybersecurity)

- **Policy coverage:** §3.4 Red-Teaming and Safety Testing mandates external red-teamer for High-Risk Features; covers prompt injection, jailbreak, demographic bias, hallucination, PII leakage; G2 gate dependency.
- **Why adequate:** Tightly aligned with Art 15(4) on robustness/cybersecurity for high-risk systems.
- **Targeted by:** Q2 (single, strong-match expected).

### A2 — GDPR Art 6 (Lawful basis)

- **Policy coverage:** §4.1 enumerates contract / legitimate interest (with documented LIA) / explicit consent.
- **Why adequate:** Standard Art 6 framing, applied correctly.

### A3 — GDPR Art 44–49 (Cross-border transfers)

- **Policy coverage:** §4.5 — adequacy decisions, SCCs (EU 2021/914 Module 2/3), TIA, EEA-residency tagging in Terraform, quarterly verification.
- **Why adequate:** Detailed and accurate. Stronger coverage than typical small-org policies.

### A4 — Incident response / breach notification timing

- **Policy coverage:** §5.3 — P0 → CAIO 15 min, DPO 2 hr, regulator 72 hr (matches GDPR Art 33).
- **Why adequate:** Direct match to GDPR Art 33's 72-hour clock.

---

## Demo question palette — gap-to-question mapping

For demo planning, pick 2–3 queries that each light up a different gap with high probability. Best mix:

| Demo slot | Query target | Hits | Drama level |
|---|---|---|---|
| Opener | Q5 (FRIA) | G1 (silent) + adjacent C1 (contradictory) | High — clear marker can verify by grep |
| Middle | Q3 (Art 22 sub-clauses) | G4 + G5 + G6 + P3 + G7 | High — shows sub-obligation granularity |
| Close | Q1 (multi-facet) | G2 + G3 + P1 + Art 22 partials | Medium — shows the system handles complexity |
| Buffer (if Streamlit hangs) | Q2 (red-teaming adequate) | A1 | Calibration — shows the system isn't always negative |
| Buffer (advanced) | Q4 (ambiguous transparency) | P2 + transparency-notice content | Shows the system handles ambiguous queries |

If the demo collapses to a single query: **Q5 (FRIA)**. Strongest single finding, fully verifiable by the marker, ties to the high-stakes deployer-as-employer story.

---

## Maintenance log

- **2026-05-04** — initial inventory built from manual policy read + grep verification of silences. 7 silences (G1–G7), 1 contradiction (C1), 7 partials (P1–P7), 4 adequates (A1–A4) catalogued.
- *Next update:* after build-completion stage 1 — record actual `match_status` produced by the chain for each gap; flag any discrepancies (system says `partial` where this doc says `silent`, etc.) for τ tuning or FLEX-1 escalation.
