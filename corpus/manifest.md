# Corpus Manifest — Novara AI Compliance Gap Analysis Project

**Snapshot date:** 2 May 2026
**Purpose:** Reproducible source material for the RAG-based compliance gap analysis system. Canonical corpus on which all evaluation results are computed.

This manifest is intended for inclusion as appendix material in the project's written report to satisfy the brief's reproducibility requirement.

---

## Summary

| Bucket | Description | Files | Words | Bytes |
|---|---|---|---|---|
| `regulation/` | External regulation: EU AI Act (Reg. 2024/1689) + UK GDPR articles 5, 6, 9, 13, 14, 22, 28, 35 | 11 | 103,621 | 2,415,073 |
| `operational/` | Operational guidance: ICO main AI guidance suite, GenAI consultation response, AI audit framework | 18 | 56,473 | 359,837 |
| `deployer/` | Fictive deployer master policy: Novara AI Governance Policy v3.1 | 2 | 3,994 | 197,432 |
| `deployer-extras/` | Fictive deployer supporting documents: 5 TalentLens-anchored documents (Model Card, DPIA, Transparency Notice, Annual Governance Report, Model Intake Assessment) | 5 | 8,343 | 55,431 |
| **Total** | | **36** | **172,431** | **3,027,773** |

## Folder structure

```
corpus/
├── manifest.json              (machine-readable manifest)
├── manifest.md                (this file)
├── regulation/                (REG)
│   ├── eu-ai-act-2024-1689.pdf       Reg (EU) 2024/1689 — Artificial Intelligence Act (419pp)
│   ├── eu-ai-act-2024-1689.txt       Extracted text (~94k words)
│   ├── uk-gdpr-articles-relevant.txt Consolidated cluster: Arts 5, 6, 9, 13, 14, 22, 28, 35
│   └── uk-gdpr-art-{N}.txt           Individual articles (8 files)
├── operational/               (OPS)
│   ├── ico-main-guidance/     ICO 'Guidance on AI and data protection' (10 chapters)
│   ├── ico-genai-consultation/ ICO Dec 2024 GenAI consultation response (6 chapters)
│   └── ico-audit-framework/   ICO AI audit toolkit (overview + governance chapter)
├── deployer/                  (DEP — Novara fictive master policy)
│   ├── novara-ai-policy-v3.1.pdf     Master policy as authored by Daria
│   └── novara-ai-policy-v3.1.txt     Extracted text
└── deployer-extras/           (DEP — Novara fictive supporting documents)
    ├── novara-talentlens-model-card.md
    ├── novara-talentlens-dpia.md
    ├── novara-talentlens-transparency-notice.md
    ├── novara-2025-ai-governance-report.md
    └── novara-talentlens-model-intake-assessment.md
```

## Regulation (REG)

| File | Date | Source | Bytes | Words | SHA-256 (16) |
|---|---|---|---|---|---|
| `regulation/eu-ai-act-2024-1689.pdf` | 2024-07-12 | [link](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689) | 1,606,488 | 0 | `0955714a0b0ab19a` |
| `regulation/eu-ai-act-2024-1689.txt` | — | [link](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689) | 740,312 | 93,565 | `5927aa360d1fa9c9` |
| `regulation/uk-gdpr-art-13.txt` | — | [link](https://gdpr-info.eu/art-13-gdpr/) | 3,216 | 526 | `94945eae1c8bf262` |
| `regulation/uk-gdpr-art-14.txt` | — | [link](https://gdpr-info.eu/art-14-gdpr/) | 5,384 | 776 | `1e659e173eb4ff23` |
| `regulation/uk-gdpr-art-22.txt` | — | [link](https://gdpr-info.eu/art-22-gdpr/) | 1,376 | 223 | `a3b18e8e212ca58f` |
| `regulation/uk-gdpr-art-28.txt` | — | [link](https://gdpr-info.eu/art-28-gdpr/) | 5,511 | 874 | `e60d6e5bcfa447a1` |
| `regulation/uk-gdpr-art-35.txt` | — | [link](https://gdpr-info.eu/art-35-gdpr/) | 4,431 | 702 | `78e04cfcc8bb75fb` |
| `regulation/uk-gdpr-art-5.txt` | — | [link](https://gdpr-info.eu/art-5-gdpr/) | 2,804 | 334 | `24412bec299ded45` |
| `regulation/uk-gdpr-art-6.txt` | — | [link](https://gdpr-info.eu/art-6-gdpr/) | 5,417 | 769 | `cd6a32c3b1b0348e` |
| `regulation/uk-gdpr-art-9.txt` | — | [link](https://gdpr-info.eu/art-9-gdpr/) | 5,595 | 802 | `e91a3930a54bf9cd` |
| `regulation/uk-gdpr-articles-relevant.txt` | 2018-05-25 | gdpr-info.eu (consolidated) | 34,539 | 5,050 | `0bc97340c9f29162` |

## Operational guidance (OPS)

| File | Date | Source | Bytes | Words | SHA-256 (16) |
|---|---|---|---|---|---|
| `operational/ico-audit-framework/01-overview.txt` | — | [link](https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/artificial-intelligence/) | 636 | 96 | `2ba684db737644bc` |
| `operational/ico-audit-framework/02-governance-accountability.txt` | — | [link](https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/artificial-intelligence/) | 20,315 | 3,100 | `833c9b142636bfda` |
| `operational/ico-genai-consultation/01-executive-summary.txt` | — | [link](https://ico.org.uk/about-the-ico/what-we-do/our-work-on-artificial-intelligence/response-to-the-consultation-series-on-generative-ai/) | 5,630 | 847 | `6dbfd13660fb3166` |
| `operational/ico-genai-consultation/02-lawful-basis-web-scraping.txt` | — | [link](https://ico.org.uk/about-the-ico/what-we-do/our-work-on-artificial-intelligence/response-to-the-consultation-series-on-generative-ai/) | 17,193 | 2,666 | `4f9e63ce0320b5a6` |
| `operational/ico-genai-consultation/03-purpose-limitation.txt` | — | [link](https://ico.org.uk/about-the-ico/what-we-do/our-work-on-artificial-intelligence/response-to-the-consultation-series-on-generative-ai/) | 8,795 | 1,352 | `7cb23d7ce38ff39e` |
| `operational/ico-genai-consultation/04-accuracy-training-data.txt` | — | [link](https://ico.org.uk/about-the-ico/what-we-do/our-work-on-artificial-intelligence/response-to-the-consultation-series-on-generative-ai/) | 10,249 | 1,554 | `1de77e08ee0174cf` |
| `operational/ico-genai-consultation/05-individual-rights-engineering.txt` | — | [link](https://ico.org.uk/about-the-ico/what-we-do/our-work-on-artificial-intelligence/response-to-the-consultation-series-on-generative-ai/) | 11,975 | 1,792 | `4f65060eda2fdbaf` |
| `operational/ico-genai-consultation/06-controllership-supply-chain.txt` | — | [link](https://ico.org.uk/about-the-ico/what-we-do/our-work-on-artificial-intelligence/response-to-the-consultation-series-on-generative-ai/) | 7,250 | 1,083 | `07dd9eafe0457c40` |
| `operational/ico-main-guidance/01-about.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 15,615 | 2,478 | `ccc3d6a34f51a7fc` |
| `operational/ico-main-guidance/02-accountability-governance.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 40,071 | 6,373 | `62bf76a8410259a6` |
| `operational/ico-main-guidance/03-transparency.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 2,091 | 353 | `bb867e4ab1cadb03` |
| `operational/ico-main-guidance/04-lawfulness.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 19,836 | 3,262 | `f54098a8543db879` |
| `operational/ico-main-guidance/05-accuracy.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 16,245 | 2,614 | `f7325067b5c79ad8` |
| `operational/ico-main-guidance/06-fairness.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 22,305 | 3,515 | `63441b8964d001d3` |
| `operational/ico-main-guidance/07-article-22-fairness.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 5,951 | 976 | `bcabd7b7ebc9f3a9` |
| `operational/ico-main-guidance/08-individual-rights.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 44,594 | 7,056 | `2b4c22f93da9fefe` |
| `operational/ico-main-guidance/09-security-data-minimisation.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 46,805 | 7,401 | `9824014d970b6fc4` |
| `operational/ico-main-guidance/10-annex-a-fairness-lifecycle.txt` | — | [link](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/) | 64,557 | 9,989 | `b7b57c944f2ad3ba` |

## Deployer master policy (DEP)

| File | Date | Source | Bytes | Words | SHA-256 (16) |
|---|---|---|---|---|---|
| `deployer/novara-ai-policy-v3.1.pdf` | 2025-03-01 (fictive) | — Fictive (Novara fabricated for project) — | 169,883 | 0 | `a80ae3a67ae5c08f` |
| `deployer/novara-ai-policy-v3.1.txt` | — | — Fictive (Novara fabricated for project) — | 27,549 | 3,994 | `215d8fbc00cbcbdb` |

## Deployer supporting documents (DEP)

| File | Date | Source | Bytes | Words | SHA-256 (16) |
|---|---|---|---|---|---|
| `deployer-extras/novara-2025-ai-governance-report.md` | 2026-02-28 (fictive) | — Fictive (Novara fabricated for project) — | 13,889 | 2,113 | `a99b9c6343316b83` |
| `deployer-extras/novara-talentlens-dpia.md` | 2025-02-12 (fictive) | — Fictive (Novara fabricated for project) — | 13,033 | 2,013 | `4bbcbda267147404` |
| `deployer-extras/novara-talentlens-model-card.md` | 2025-01-15 (fictive) | — Fictive (Novara fabricated for project) — | 12,749 | 1,790 | `9aef163f6b38c027` |
| `deployer-extras/novara-talentlens-model-intake-assessment.md` | 2025-01-15 (fictive) | — Fictive (Novara fabricated for project) — | 9,744 | 1,489 | `e2f2d1809b704904` |
| `deployer-extras/novara-talentlens-transparency-notice.md` | 2025-03-01 (fictive) | — Fictive (Novara fabricated for project) — | 6,016 | 938 | `ebd621b0001753ce` |

## Notes on document selection and known caveats

**On the AI Act PDF.** Fetched as the EU Council consolidated version (PE-CONS 24/24), textually identical to Regulation (EU) 2024/1689 as published in the Official Journal of the European Union on 12 July 2024. EUR-Lex is the canonical legal publisher; cite EUR-Lex for academic submission.

**On UK GDPR text source.** Article texts are taken from gdpr-info.eu, which mirrors the EU GDPR text. UK GDPR articles share numbering and substantive text with EU GDPR for the cluster used here. UK-specific implementations are referenced separately via the Data Protection Act 2018 (not in this corpus).

**On ICO main guidance recency.** The ICO main 'Guidance on AI and data protection' carries a January 2026 banner indicating it is under review for the Data (Use and Access) Act 2025; treat as the current authoritative version subject to that explicit caveat.

**On Novara fictive documents.** All Novara-named documents are fabricated for academic purposes. Novara AI, Inc. is a fictional company. The supporting documents are designed to contain realistic compliance gaps for the gap-analysis system to surface. None of the people, products, customers, or events described are real.

## Refresh and versioning policy

This corpus is **frozen** as of 2 May 2026 for the duration of evaluation runs. Any updates to source documents (regulatory amendments, ICO guidance updates, revisions to fictive Novara documents) require a new versioned snapshot with a fresh manifest. SHA-256 hashes recorded above are the integrity reference; re-hashing the live files should produce these exact values.

---

*Manifest generated 2 May 2026. Total: 36 files, 172,431 words, 3,027,773 bytes (~2.9 MB).*