# Novara TalentLens — Model Intake Assessment

**CONFIDENTIAL — INTERNAL USE ONLY**

| Document Field | Value |
|---|---|
| Document ID | NAI-MIA-0042 |
| Template Reference | NAI-TMPL-0031 (Model Intake Assessment Template, v2.1) |
| Classification | Confidential — Internal Use Only |
| Subject Product | TalentLens |
| Foundation Model | Mistral-Large-2 (commercial license) |
| Fine-tuned Variant | NovaraNet-HR-v2.3 |
| Assessment Date | 15 January 2025 |
| Assessor | Product AI Champion, TalentLens squad |
| Engineering Lead Sign-off | 15 January 2025 |
| CAIO Counter-sign-off | 22 January 2025 |
| Outcome | **Approved for Production** |

This Model Intake Assessment is conducted in accordance with NAI-POL-0042 §3.1 (Model Selection and Procurement) prior to the integration of the NovaraNet-HR-v2.3 fine-tuned model into TalentLens production. Each section corresponds to the standard intake assessment checklist.

---

## 1. Model Identification

| Field | Value |
|---|---|
| Foundation model name | Mistral-Large-2 |
| Foundation model provider | Mistral AI |
| Foundation model version reviewed | 2.1.0 (released October 2024) |
| Parameter count | 70 billion (decoder-only transformer) |
| Architecture | Mistral-style decoder-only with grouped-query attention |
| Source of foundation model weights | Mistral AI commercial download with signed agreement |
| Local fine-tune name | NovaraNet-HR-v2.3 |
| Fine-tune training data | Curated subset of Novara HR-domain corpus (see §3 below) |
| Fine-tune methodology | SFT followed by RLHF for ranking-quality alignment |
| Final model size on disk | 142 GB (FP16); 38 GB (4-bit quantised inference variant) |

---

## 2. Licensing and Intellectual Property

### 2.1 License confirmation

The Mistral-Large-2 commercial license, executed between Novara AI and Mistral AI on 18 September 2024 (Master Agreement reference: MIST-NAI-2024-001), permits the following:

- ✓ Commercial use in products and services
- ✓ Fine-tuning on proprietary data
- ✓ Deployment in production systems
- ✓ Output commercialisation without per-output royalty
- ✓ Bundling fine-tuned weights with Novara products under appropriate confidentiality

The license **does not** permit:

- Redistribution of foundation model weights to third parties
- Reverse engineering or extraction of model weights
- Use for model-distillation aimed at producing a competing foundation model

Reviewed by: Legal team (Senior IP Counsel signed off 12 January 2025).

### 2.2 Output IP and copyright considerations

Novara has reviewed the indemnification provisions of the Mistral commercial license. Outputs of NovaraNet-HR-v2.3 fall within the indemnified scope subject to applicable customer-side filtering (per NAI-POL-0033 §4.2). For TalentLens use case (CV assessment output), output is novel structured assessment text rather than verbatim training-data reproduction; copyright risk is assessed as low.

---

## 3. Data Provenance Review

### 3.1 Foundation model training data

Mistral AI's data lineage documentation provided under NDA was reviewed and accepted. Documentation covers approximately 8 trillion tokens of pretraining data with declared sources (web crawl, code repositories, books, academic literature). Specific dataset-level provenance for individual training examples is not available — this is consistent with industry practice for foundation model providers and is accepted as a known limitation.

### 3.2 Fine-tuning data

Fine-tuning data was sourced and prepared per NAI-POL-0042 §3.2. Three categories:

| Source | Description | Volume | Lawful basis |
|---|---|---|---|
| Public CV datasets | Publicly available CV-job-description pairs from academic and open-research sources | ~1.2M pairs | Original license (CC-BY and academic licenses) |
| Licensed third-party HR data | Acquired under commercial Data Licensing Agreements | ~150K pairs | Contract with provider warrants of lawful collection |
| Internal customer-feedback data | Anonymised recruiter assessments under DPA opt-in | ~75K examples | Customer DPA opt-in (Article 6(1)(f) legitimate interests) |

All datasets registered in Novara Data Catalogue (Collibra) with Data Engineering quality scores assigned per NAI-POL-0042 §3.2.

### 3.3 Data quality and known issues

Data quality scoring identified a sex-distribution skew (58% male / 42% female) in source data. Mitigation: demographic-balanced sampling applied during fine-tuning (see Model Card §5.3). No other significant data quality issues identified during ingest.

---

## 4. Security Posture Review

### 4.1 Foundation model provider security

Mistral AI's SOC 2 Type II report (period: October 2023 — September 2024) was reviewed and confirmed satisfactory. Key controls:

- Model weight integrity: cryptographic signing of distributed weights ✓
- Inference endpoint security: TLS 1.3 minimum, encryption at rest ✓
- Access controls: role-based access, audited admin access ✓
- Incident response: documented IR plan ✓
- Vulnerability management: monthly scanning, time-bounded patching ✓

### 4.2 Novara's deployment security

NovaraNet-HR-v2.3 is deployed within Novara's standard SOC 2 Type II–audited infrastructure (eu-west-1 primary, us-east-1 secondary). Inference endpoint covered by Novara's standard security controls per NAI-POL-0018 (IT Security Policy).

Tenant isolation at storage and inference layer confirmed by Infrastructure Security review on 14 January 2025.

### 4.3 Model weights security

Production model weights stored in Novara's encrypted artefact store with restricted access; only AI Engineering deploy-bot has read access for production inference servers. Counter-signed access logs reviewed quarterly.

---

## 5. Export Controls

### 5.1 Export Administration Regulations review

Reviewed by Legal team. Mistral-Large-2 is not subject to U.S. EAR controls as the foundation model originates from a French (EU) entity. Novara's deployment to US (us-east-1) and EU (eu-west-1) regions does not engage EAR re-export concerns.

### 5.2 EU export controls

EU dual-use export regulation reviewed; current generation foundation models are not subject to EU dual-use export controls for cross-EU deployment. Customers in restricted jurisdictions (per Novara's Sanctions Compliance Policy) are excluded from TalentLens onboarding.

---

## 6. Performance Benchmarks

The performance of NovaraNet-HR-v2.3 was benchmarked against the validation criteria for TalentLens prior to production approval. All criteria passed.

| Benchmark | Target | Observed | Pass |
|---|---|---|---|
| Top-1 ranking accuracy on internal validation | ≥ 0.80 | 0.847 | ✓ |
| Top-3 ranking accuracy | ≥ 0.90 | 0.923 | ✓ |
| Latency p50 (per CV inference) | ≤ 3.0 sec | 1.8 sec | ✓ |
| Latency p99 | ≤ 7.0 sec | 4.2 sec | ✓ |
| Cost per evaluation (USD) | ≤ $0.020 | $0.011 | ✓ |
| Throughput per inference instance | ≥ 100 CVs/min | 280 CVs/min | ✓ |
| Demographic parity (sex) | ≥ 0.85 | 0.94 | ✓ |
| Demographic parity (age band) | ≥ 0.85 | 0.92 | ✓ |
| Equalised odds (sex) | ≥ 0.85 | 0.91 | ✓ |
| Equalised odds (age band) | ≥ 0.85 | 0.88 | ✓ |
| Hallucination rate on validation | ≤ 5% | 2.7% | ✓ |
| PII leakage rate from training data | 0% | 0% | ✓ |

---

## 7. Risk Classification

This Intake Assessment classifies NovaraNet-HR-v2.3 as deployed in TalentLens as: **Standard AI Feature**.

The classification basis is:

- TalentLens is a decision-support system; final hiring decisions remain with the Customer's recruiter (HITL Level 2 mandatory)
- Output is structured assessment text, not direct decision
- TalentLens does not directly substitute for human decision-making about employment outcomes

This classification was reviewed by the Product AI Champion in consultation with Legal and the DPO per NAI-POL-0042 Appendix A.

---

## 8. Sign-Off

| Role | Name (representative) | Date | Decision |
|---|---|---|---|
| Product AI Champion (TalentLens squad) | (Champion) | 15 January 2025 | Recommended for approval |
| Engineering Lead | (Eng Lead) | 15 January 2025 | Approved |
| Data Privacy Officer | Maeve O'Connor | 18 January 2025 | DP review complete |
| AI Safety Review Board | (Chair) | 20 January 2025 | Reviewed |
| Chief AI Officer | (CAIO) | 22 January 2025 | Approved for Production |

---

## 9. Production Approval Conditions

This approval is contingent on the following conditions being met during production:

1. Quarterly bias audit per NAI-DOC-0027 (next due 31 May 2025)
2. Continuous drift monitoring per NAI-POL-0042 §3.3 G4 requirements
3. HITL Level 2 enforced at Customer deployment (sampled review of ≥ 5% or 500 outputs/week)
4. Annual external audit per NAI-POL-0042 §5.4
5. DPIA NAI-DPIA-0023 reviewed and updated annually
6. Model Card NAI-MC-0007 reviewed and updated at each version release
7. P0/P1 incidents trigger immediate suspension and AI Ethics & Safety Committee review

This approval is valid for the lifetime of the v2.3 model version. Major version updates require a new Intake Assessment.

---

## 10. Related Documents

| Document ID | Title |
|---|---|
| NAI-POL-0042 | AI Product Development, Privacy & Governance Policy v3.1 |
| NAI-TMPL-0031 | Model Intake Assessment Template (master template) |
| NAI-MC-0007 | TalentLens Model Card v2.3 |
| NAI-DPIA-0023 | TalentLens DPIA v1.4 |
| NAI-POL-0018 | IT Security Policy |
| NAI-POL-0033 | TalentLens Acceptable Use Policy |
| NAI-DOC-0027 | Bias Audit Methodology |
| MIST-NAI-2024-001 | Mistral AI / Novara Master Agreement |

---

**END OF DOCUMENT**

NAI-MIA-0042 v1.0 • © 2025 Novara AI, Inc. All rights reserved. Confidential — Internal Use Only.
