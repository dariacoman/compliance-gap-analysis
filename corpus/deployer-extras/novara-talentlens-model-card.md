# Novara TalentLens — Model Card

**CONFIDENTIAL — INTERNAL USE ONLY**

| Document Field | Value |
|---|---|
| Document ID | NAI-MC-0007 |
| Product | TalentLens |
| Model Version | NovaraNet-HR-v2.3 |
| Card Version | 2.3 (matches model version) |
| Classification | Confidential — Internal Use Only |
| Effective Date | 15 January 2025 |
| Next Review Date | 15 January 2026 |
| Card Owner | VP, AI Engineering |
| Approved By | Chief AI Officer (CAIO) |

This Model Card complies with NAI-POL-0042 §3.3 (Model Evaluation Requirements) and follows the Mitchell et al. (2019) Model Card framework as adapted in Novara's internal documentation standard NAI-DOC-0023.

---

## 1. Model Details

**Model name:** NovaraNet-HR-v2.3

**Model type:** Fine-tuned large language model with structured-output decoder, deployed as a CV-screening and candidate-ranking inference service.

**Model architecture:** Decoder-only transformer (Mistral-Large-2 base, 70B parameters). Fine-tuned with supervised fine-tuning (SFT) on proprietary HR-domain instruction data, followed by Reinforcement Learning from Human Feedback (RLHF) for ranking-quality alignment.

**Provider:** Novara AI, Inc. (fine-tuned and operated). Base foundation model licensed from Mistral AI under commercial agreement permitting fine-tuning and commercialisation.

**Model status:** Production. Generally Available (GA) since October 2023. Current production version v2.3 deployed January 2025 following Gate G3 (Limited GA) and Gate G4 (Full GA) approval per NAI-POL-0042 §3.3.

**Date of release:** 15 January 2025 (v2.3); Initial GA October 2023 (v1.0).

**Owner team:** Novara AI Engineering — TalentLens product squad (8 engineers, 2 ML scientists, 1 product manager, 1 Product AI Champion per NAI-POL-0042 §5.1).

**Training framework:** PyTorch 2.4 with HuggingFace Transformers and TRL (Transformer Reinforcement Learning). Inference via vLLM 0.6.x deployed on NVIDIA H100 GPU clusters in eu-west-1 (Ireland) primary region.

**Approver:** Chief AI Officer signed off Model Intake Assessment NAI-MIA-0042 on 22 January 2025 per NAI-POL-0042 §3.1.

---

## 2. Intended Use

### 2.1 Primary use case

TalentLens is designed to assist enterprise HR and recruitment teams in screening and ranking candidate applications for relevant skills against a job description. The system operates in two primary modes:

- **Screening mode** — given a candidate CV and a job description, produce a structured assessment of skill alignment, identified strengths, and identified gaps relative to the role requirements.
- **Ranking mode** — given a list of candidate CVs and a job description, produce a relative ordering of candidates by skill alignment.

The system is intended as a *decision-support tool* for human recruiters, not as an autonomous decision-maker. Output is presented with confidence scores and supporting reasoning; final decisions on shortlisting, interviewing, or rejection rest with the recruiter.

### 2.2 Out-of-scope uses

TalentLens is **not** intended for:

- Final hiring decisions made without human review
- Medical or psychological assessment of candidates
- Termination decisions or performance management of existing employees
- Biometric identification or facial recognition of candidates
- Salary determination or compensation recommendations
- Background checks, criminal history evaluation, or credit assessment
- Visa eligibility or right-to-work determinations

Customers using TalentLens for any out-of-scope use case are in violation of the TalentLens Acceptable Use Policy (NAI-POL-0033) and the platform Terms of Service.

### 2.3 Target users

Enterprise HR teams, internal recruiters, and external recruitment agencies serving enterprise customers. Typical deployment context: a recruiter using TalentLens via Novara's web interface or API integration with their Applicant Tracking System (ATS), reviewing 50–200 candidate applications per role.

---

## 3. Training Data

### 3.1 Data sources

NovaraNet-HR-v2.3 was fine-tuned on three categories of training data:

| Category | Source | Approximate size |
|---|---|---|
| Anonymised CV–job-description pairs | Aggregated from publicly available CV datasets and licensed third-party HR data providers | ~1.2 million pairs |
| Synthetic CV–assessment pairs | LLM-generated using Mistral-Large-2 with rejection sampling against quality criteria | ~400,000 pairs |
| Recruiter feedback data | Anonymised recruiter assessments from Novara's enterprise customers under DPA opt-in | ~75,000 examples |

All training datasets are registered in Novara's centralised Data Catalogue (Collibra instance) per NAI-POL-0042 §3.2. Each dataset entry includes source, collection method, legal basis, personal-data classification, and data quality score.

### 3.2 Data composition

Training data composition has the following demographic distribution (computed on the subset where demographic markers are inferable from CVs):

- **Geography of origin (CV origin region)**: 60% EU/UK; 25% North America; 10% Asia-Pacific; 5% other
- **Inferred sex distribution**: 58% male; 42% female (reflects source-data origin skew)
- **Inferred age distribution**: 22% age 18–25; 41% age 26–35; 27% age 36–45; 8% age 46–55; 2% age 56+
- **Industries represented**: Technology and software (38%); Financial services (18%); Professional services (12%); Healthcare (9%); Manufacturing (7%); Retail (6%); Other (10%)

### 3.3 Data preprocessing

- Direct identifiers (full name, email, phone number, national ID, IP address, residential address) removed via Novara's standard PII redaction pipeline (NAI-DOC-0019)
- Resume-style formatting normalised
- CVs longer than 4,000 tokens truncated; CVs shorter than 200 tokens excluded
- Duplicate detection using fuzzy hashing; ~3.4% duplicates removed
- Quality-score filtering using internal completeness heuristic; scores below 0.6 excluded

### 3.4 Data licensing and consent

Public datasets are used under their original licenses (predominantly CC-BY and academic-research licenses). Third-party licensed data is acquired under commercial data-licensing agreements that include warranties of lawful collection from the original data providers. Customer-contributed recruiter feedback data is processed under signed Data Processing Agreements (DPAs) including AI Training Exhibits as required by NAI-POL-0042 §3.2.

---

## 4. Performance Metrics

### 4.1 Primary task metrics

Performance is measured against a held-out internal validation set of 50,000 CV–job-description pairs with human-labelled "fit" assessments by senior recruiters.

| Metric | Value | Notes |
|---|---|---|
| Top-1 ranking accuracy | 0.847 | Compared against single recruiter judgement |
| Top-3 ranking accuracy | 0.923 | Top 3 candidates contain the recruiter's top pick |
| Skill-match precision | 0.871 | Identified skills present in CV |
| Skill-match recall | 0.812 | Skills mentioned in CV identified by system |
| Mean inter-rater agreement (model vs. recruiter) | Cohen's κ = 0.71 | Substantial agreement per Landis & Koch |

### 4.2 Latency and operational performance

| Metric | Value |
|---|---|
| Mean inference latency (p50) | 1.8 seconds per CV |
| p99 inference latency | 4.2 seconds per CV |
| Throughput per inference instance | ~280 CVs/minute |
| Cost per evaluation (USD-equivalent) | $0.011 per CV |
| Maximum context window | 16,384 tokens (CV + job description + system prompt) |

### 4.3 Drift monitoring

NovaraNet-HR-v2.3 has been deployed since 15 January 2025. Drift monitoring against the launch baseline is conducted weekly by the AI Safety Review Board (NAI-POL-0042 §5.1). As of 28 February 2025, no severity-1 or severity-2 drift incidents have been recorded; minor performance variance (±2.1% on top-1 ranking accuracy) is within expected noise.

---

## 5. Fairness Analysis

### 5.1 Methodology

Fairness analysis follows Novara's internal Bias Audit Methodology (NAI-DOC-0027), which implements demographic-parity and equalised-odds testing across measurable protected characteristics. Testing is conducted by the AI Safety Review Board prior to each major version release.

### 5.2 Results

| Protected characteristic | Demographic parity (P_demo) | Equalised odds (E_odd) | Notes |
|---|---|---|---|
| Sex (binary, male/female) | 0.94 | 0.91 | Within Novara's internal 0.85 threshold |
| Age band (under 35 vs. 35+) | 0.92 | 0.88 | Within threshold |

### 5.3 Bias mitigations applied

The following mitigations were applied during NovaraNet-HR-v2.3 fine-tuning:

- Demographic-balanced sampling during SFT to reduce sex-distribution skew in training data
- Counterfactual data augmentation: 8% of training pairs include sex-swapped counterfactual variants
- Output-side constraint: the system is instructed via system prompt not to consider age, sex, or other protected characteristics in ranking justifications
- Post-hoc calibration on the held-out validation set

### 5.4 Limitations of fairness analysis

Demographic-parity scores are computed on inferred demographic markers (where derivable from CV content). Self-reported demographic data is not available for the validation set, so reported fairness metrics rely on imperfect demographic-inference proxies.

---

## 6. Known Limitations

- **Performance variance across applicant demographics.** Performance may vary across different candidate populations; specifics of where variance is highest are not separately reported here.
- **Language coverage.** Optimal performance on English-language CVs. Performance on non-English CVs reflects only the small non-English subset present in training data; non-English deployment is not currently recommended.
- **Industry coverage.** Strongest performance on Technology, Financial Services, and Professional Services roles (which are over-represented in training data). Performance on more specialised verticals (e.g., creative arts, public sector) has not been separately benchmarked.
- **Resume format dependency.** Standard chronological CV formats (the dominant format in EU/US training data) are handled best. Functional, hybrid, or unusual CV formats may produce less reliable output.
- **Rare or emerging roles.** Roles with little representation in training data (e.g., very recent technology roles, niche industry positions) may be assessed less reliably.
- **Calibration over time.** As role definitions evolve in fast-moving industries, the model's understanding may lag market reality. Drift monitoring captures aggregate drift but not domain-specific drift in individual roles.

---

## 7. Deployment Recommendations

### 7.1 Required configuration

- **Human-in-the-Loop level**: Level 2 — Sampled Review (per NAI-POL-0042 §3.5). A statistically significant random sample (minimum 5% of outputs or 500 outputs per week, whichever is greater) must be reviewed by a qualified human recruiter.
- **HITL reviewer role**: customer's senior recruiter or hiring manager, with documented training on TalentLens output interpretation
- **Monitoring**: customer must enable Novara's standard usage and drift monitoring dashboard
- **Audit log retention**: minimum 12 months for non-PII inference logs, per Novara's standard retention schedule (NAI-POL-0042 §4.4)

### 7.2 Customer responsibilities

Customer organisations deploying TalentLens are responsible for:

- Configuring HITL review processes consistent with NAI-POL-0042 §3.5
- Providing TalentLens output to candidates only after recruiter review
- Conducting customer-side data protection compliance assessment
- Honouring data subject rights requests received from candidates whose CVs are processed
- Compliance with sector-specific employment law (e.g., EEOC requirements for US deployments)

### 7.3 Not recommended for

- Deployment without HITL review (Level 3 alone is insufficient for TalentLens)
- High-volume automatic rejection workflows where >10% of candidates are rejected without recruiter review
- Customer markets or jurisdictions without an established HR review function

---

## 8. References and Related Documents

| Document ID | Title |
|---|---|
| NAI-POL-0042 | AI Product Development, Privacy & Governance Policy v3.1 |
| NAI-MIA-0042 | TalentLens Model Intake Assessment |
| NAI-DPIA-0023 | TalentLens Data Protection Impact Assessment |
| NAI-TN-0011 | TalentLens Customer Transparency Notice |
| NAI-POL-0033 | TalentLens Acceptable Use Policy |
| NAI-DOC-0019 | PII Redaction Pipeline Specification |
| NAI-DOC-0023 | Novara Model Card Internal Standard |
| NAI-DOC-0027 | Bias Audit Methodology |

---

**END OF DOCUMENT**

NAI-MC-0007 v2.3 • © 2025 Novara AI, Inc. All rights reserved. Confidential — Internal Use Only.
