# Novara AI, Inc. — 2025 Annual AI Governance Report

| Document Field | Value |
|---|---|
| Document ID | NAI-RPT-2025-AI |
| Reporting Period | 1 January 2025 — 31 December 2025 |
| Document Version | 1.0 (Final) |
| Classification | Confidential — Internal Use Only (Board distribution) |
| Issued | 28 February 2026 |
| Author | Chief AI Officer (CAIO) |
| Reviewed By | AI Ethics & Safety Committee; Audit Committee of the Board |
| Approved By | Executive Leadership Team |

This Annual Report documents Novara AI's AI governance posture for the calendar year 2025. It is prepared in accordance with NAI-POL-0042 §5.1 (AI governance roles and committees) and §5.4 (External Audits and Regulatory Compliance), and is presented to the Board of Directors and made available to enterprise customers and external auditors on request.

---

## Executive Summary

In 2025, Novara AI continued to scale our enterprise AI platform across HR-tech, financial services, healthcare, and legal verticals. Headline figures for the reporting year:

- **47 active enterprise customers** at year-end (up from 31 in 2024)
- **8 production AI products**, of which 6 are generally available and 2 are in Limited GA
- **One major model release** (NovaraNet-HR-v2.3, January 2025); two minor releases (NovaraScore-FS-v1.4, NovaraDx-MED-v0.9 Limited GA)
- **Zero P0 (Critical) AI incidents** reported during the year
- **Three P1 (High) incidents**, all resolved within target SLA timeframes
- **Eleven P2 (Medium) incidents**, of which eight are closed and three remain in active remediation
- **External AI audit completed** by BlueRock Compliance Audit Ltd. in December 2025 with two material findings, both with remediation plans approved
- **EU AI Act risk classification:** Limited-Risk for the current product portfolio (subject to annual re-assessment)

The year saw significant regulatory development — the Data (Use and Access) Act 2025 came into force in the United Kingdom, ongoing implementation of the EU AI Act continued, and the ICO issued updated guidance on AI in research, archiving and statistics. Novara has reviewed each development and updated relevant policies accordingly.

The headline AI governance posture remains: principled, accountable, and audited. We are well-positioned for the regulatory environment we currently face. The next year's priorities focus on extending our governance maturity to new product launches, deepening our bias-auditing methodology, and preparing for anticipated regulatory developments in 2026.

---

## 1. AI Portfolio Overview

### 1.1 Product distribution at year-end

| Product | Vertical | Status | First GA | Latest Version | EU AI Act Classification |
|---|---|---|---|---|---|
| TalentLens | HR-tech | GA | October 2023 | v2.3 (Jan 2025) | Limited-Risk |
| NovaraScore-FS | Financial services credit decisioning | GA | March 2024 | v1.4 (June 2025) | Limited-Risk |
| NovaraDx | Healthcare clinical decision support | Limited GA | November 2024 | v0.9 (December 2025) | Limited-Risk |
| LegalLens | Legal document review | GA | August 2022 | v3.7 (April 2025) | Limited-Risk |
| ContentGuard | Content moderation for enterprise platforms | GA | February 2023 | v2.1 (October 2025) | Limited-Risk |
| RetailMatch | Customer-segmentation for retail vertical | GA | June 2023 | v1.8 (May 2025) | Limited-Risk |
| ServiceFlow | Workflow automation copilot | GA | January 2024 | v1.5 (September 2025) | Limited-Risk |
| InsightDeck | Business intelligence assistant | Limited GA | October 2025 | v0.7 (December 2025) | Limited-Risk |

### 1.2 Headline operational metrics

- **Combined inference volume:** ~31 million inferences across all products in 2025
- **Combined customer-facing system uptime:** 99.94% (TalentLens), 99.97% (LegalLens, GAged), aggregate 99.91% across portfolio
- **Total AI-related infrastructure spend:** undisclosed in this report (see Audit Committee detailed financial annex)

### 1.3 Foundation model dependencies

Across the portfolio, Novara fine-tunes from three foundation model families: Mistral (Mistral Large family — TalentLens, NovaraScore-FS, ContentGuard, ServiceFlow, RetailMatch); LLaMA (Meta's Llama 3.1 family — LegalLens, InsightDeck); and Anthropic Claude API (NovaraDx for clinical reasoning). Each foundation model relationship is governed by a Model Intake Assessment per NAI-POL-0042 §3.1, with refresh on each major version change.

---

## 2. AI Risk Register Summary

### 2.1 Risk register status

The AI Risk Register (Jira project AI-RISK) had the following status at year-end 2025:

| Risk Category | Open at Y/E 2024 | New in 2025 | Resolved in 2025 | Open at Y/E 2025 |
|---|---|---|---|---|
| Model Safety | 8 | 12 | 14 | 6 |
| Privacy / Regulatory | 11 | 7 | 9 | 9 |
| IP & Copyright | 4 | 3 | 4 | 3 |
| Third-Party Model Risk | 6 | 4 | 5 | 5 |
| Operational Reliability | 9 | 14 | 15 | 8 |
| Adversarial / Abuse | 5 | 6 | 4 | 7 |
| **Total** | **43** | **46** | **51** | **38** |

### 2.2 Top three risk categories at year-end

1. **Privacy / Regulatory (9 open).** Largest single residual: customer-side variation in DSR-fulfilment processes for AI-mediated decisions. Owned by DPO; review cadence monthly.
2. **Operational Reliability (8 open).** Largest single residual: drift monitoring sensitivity calibration across the multi-product portfolio. Owned by Head of SRE; review cadence weekly.
3. **Adversarial / Abuse (7 open).** Largest single residual: emerging prompt-injection attack patterns observed in ContentGuard during late 2025. Owned by Head of Security; continuous review.

### 2.3 Remediation cadence

The AI Ethics & Safety Committee meets monthly to review the AI Risk Register; ad hoc convenings have been triggered three times in 2025 in response to P0 false-alarm and P1 escalations. Audit-committee-level review of the consolidated register occurs quarterly.

---

## 3. AI Incidents in 2025

### 3.1 Incident summary

| Severity | Count | Mean time to remediation | Notes |
|---|---|---|---|
| P0 (Critical) | 0 | N/A | None reported |
| P1 (High) | 3 | 4.2 business days | All within SLA |
| P2 (Medium) | 11 | 9.6 business days | 8 closed; 3 in active remediation |
| P3 (Low) | 47 | N/A | Logged in AI Risk Register; bi-weekly review |

### 3.2 Notable incidents

- **P1-2025-04 (April 2025).** ContentGuard model produced offensive output classifications under specific adversarial prompt conditions. Remediation: model retrained with adversarial-prompt-resistance fine-tuning; rolled out within target SLA.
- **P1-2025-09 (September 2025).** Brief drift incident in LegalLens output accuracy following a model update; identified within drift-monitoring window. Remediation: rollback to previous version, retraining, redeployment.
- **P1-2025-12 (December 2025).** RetailMatch confidence-score miscalibration affected ranking quality on a small subset of customer segments. Identified during quarterly drift audit. Remediation: post-hoc calibration update.

All P1 incidents underwent blameless post-mortem within 5 business days per NAI-POL-0042 §5.3.

---

## 4. Audit Findings

### 4.1 Annual external audit (BlueRock Compliance Audit Ltd., December 2025)

BlueRock Compliance conducted Novara's annual third-party AI audit per NAI-POL-0042 §5.4. Audit scope covered: compliance with NAI-POL-0042; ISO/IEC 42001:2023 alignment; UK GDPR / EU GDPR Article 22 compliance; EU AI Act obligations applicable to Novara's risk classification; SOC 2 Type II Trust Services Criteria as they apply to AI processing.

**Audit verdict: Substantially compliant with two material findings.**

### 4.2 Material findings

**Finding 1 — Documentation of Article 6 lawful-basis assessment for AI training data.** BlueRock noted that while Novara's training data is registered in the Data Catalogue per NAI-POL-0042 §3.2 with declared lawful basis, the documented legitimate-interest assessments (LIAs) lacked the depth of balancing-test articulation required to meet Article 6(1)(f) audit standards.

*Remediation:* Legal team revising LIA template (target: Q2 2026); existing LIAs reviewed and updated.

**Finding 2 — Bias audit demographic coverage breadth.** BlueRock noted that Novara's bias auditing methodology (NAI-DOC-0027) covers sex and age demographics but does not extend systematically to race, religion, disability, or sexual orientation. While noting that demographic-inference for these characteristics is technically harder, BlueRock flagged this as a gap relative to comprehensive AI fairness expectations.

*Remediation:* AI Safety Review Board commissioning expanded methodology (target: Q3 2026 implementation, Q4 2026 first audit).

### 4.3 Remediation plan status

Both material findings have remediation plans approved by the CAIO and the AI Ethics & Safety Committee. Remediation plans were submitted to BlueRock within the contractual 60-day window (per NAI-POL-0042 §5.4). Status will be reviewed at the H1 2026 AI Ethics & Safety Committee meeting.

---

## 5. Regulatory Monitoring

Novara monitors regulatory developments in AI, data protection, and sector-specific rules on a quarterly cadence per NAI-POL-0042 §5.4. The following developments were tracked in 2025:

### 5.1 EU AI Act implementation

- **Article 5 (Prohibited Practices)** — Novara confirmed via Legal review that no Novara product engages prohibited practices.
- **Article 6 (Risk Classification)** — Legal continues to assess Novara's portfolio as Limited-Risk; this is reviewed annually.
- **Article 50 (Transparency)** — Novara updated user-facing language across the portfolio in Q3 2025 to enhance disclosure of AI-generated content.
- **GPAI obligations** — Not directly applicable as Novara is not a GPAI provider; relationship with foundation model providers governed by commercial agreements.

### 5.2 UK regulatory developments

- **Data (Use and Access) Act 2025** — Came into force in June 2025. Legal team reviewed implications for Novara's UK operations.
- **UK AI White Paper / AI Bill** — No statutory AI bill enacted in 2025; principles-based approach continues. Novara monitors developments and is prepared for compliance requirements as they emerge.

### 5.3 ICO guidance updates

- **AI and data protection guidance** — Under review by ICO due to DUAA 2025; Novara continues to apply current guidance until update is published.
- **Generative AI consultation response** — Novara reviewed against current practices; no operational changes required.

### 5.4 Other developments

- US NIST AI Risk Management Framework version updates monitored
- FTC guidance on AI in employment monitored (relevant to TalentLens)
- Sector regulators (FCA, MHRA) AI guidance monitored as applicable

---

## 6. AI Governance Maturity

### 6.1 Training and certification

| Course | Population | Completion rate Q4 2025 |
|---|---|---|
| AI Ethics Foundations (NAI-LRN-0041) | All AI-involved staff | 96.4% |
| Data Privacy in AI Pipelines (NAI-LRN-0042) | Engineering, data science, PM | 91.7% |
| Secure AI Development (NAI-LRN-0043) | ML engineers, MLOps | 88.3% |
| Red-Team Practitioner (NAI-LRN-0044) | Designated red-team members | 100% |

### 6.2 Governance committee operations

- **AI Ethics & Safety Committee:** 12 monthly meetings + 3 ad hoc convenings
- **AI Safety Review Board:** 26 bi-weekly meetings, all chaired
- **DPO consultations:** 50+ engagements with AI product teams during the year
- **Product AI Champions network:** 8 designated champions across product squads

### 6.3 External engagement

- ISO/IEC 42001:2023 certification work commenced; gap-assessment phase complete; targeted certification in 2026
- Novara contributed to the Mistral Foundation Model GPAI Code of Practice consultation
- Three Novara staff served on industry working groups on AI fairness and HR-tech ethics

---

## 7. Looking Ahead — 2026 Priorities

### 7.1 Governance maturity

- Complete remediation of both material findings from the BlueRock audit
- Achieve ISO/IEC 42001:2023 certification
- Expand bias audit methodology to cover additional protected characteristics
- Extend governance committee scope to cover anticipated 2026 product launches

### 7.2 Regulatory readiness

- Prepare for any UK AI Bill requirements that may emerge in 2026 King's Speech
- Monitor EU AI Act implementing acts and standards as they are issued
- Update internal documentation to reflect any ICO guidance revisions

### 7.3 Product safety enhancements

- Deepen drift-monitoring methodology with multi-modal signals
- Enhance prompt-injection resistance testing across the portfolio
- Continued investment in red-teaming both internally and via external partners

---

## 8. Acknowledgements and Sign-off

This Report has been prepared by the Chief AI Officer in consultation with the AI Ethics & Safety Committee, the Data Protection Officer, and the AI Safety Review Board, and reflects governance activity across Novara AI's full product portfolio for the calendar year 2025.

Approval and distribution:

- Approved by the Executive Leadership Team: 25 February 2026
- Reviewed by the Audit Committee of the Board: 27 February 2026
- Issued: 28 February 2026

The next Annual AI Governance Report (covering calendar year 2026) is due by 28 February 2027.

---

## 9. Related Documents

| Document ID | Title |
|---|---|
| NAI-POL-0042 | AI Product Development, Privacy & Governance Policy v3.1 |
| NAI-POL-0009 | Data Subject Rights Procedure |
| NAI-DOC-0017 | AI Risk Severity Matrix |
| NAI-DOC-0027 | Bias Audit Methodology |
| NAI-RPT-2024-AI | 2024 Annual AI Governance Report (predecessor) |
| BlueRock-AUD-2025-NAI | External AI Audit Report — Novara AI 2025 (auditor's confidential file) |

---

**END OF DOCUMENT**

NAI-RPT-2025-AI v1.0 • © 2026 Novara AI, Inc. All rights reserved. Confidential — Internal Use Only.
