# Corpus Specification (v2) — AI Compliance Gap Analysis Project

*What goes into the project corpus, where it comes from, how it's organised, and how it gets refreshed. Companion to `v2_project_brief.md` and `v2_implementation_plan.md`.*

---

## 1. Purpose and scope

The corpus is the substrate the system reads and reasons over. For an AI compliance gap analysis system, the corpus has four logical buckets, each playing a distinct role in the gap analysis:

| Bucket | Role | Purpose |
|---|---|---|
| `regulation` | What the law requires | The "should" side of the analysis — primary sources of legal obligation |
| `operational` | How regulators interpret the law | Translates abstract regulation into concrete operational expectations |
| `deployer` (Novara policy) | What the company says it does | The fictive Novara AI Governance Policy v3.1 — the central object of analysis |
| `deployer-extras` (Novara supporting docs) | How the company operationalises the policy | The fictive Model Card, DPIA, Transparency Notice, Annual Governance Report, Model Intake Template — see `v2_supporting_documents_brief.md` |

The system queries against all four; the residual-risk register surfaces gaps between what the regulation expects, what regulator guidance elaborates, and what the deployer's policy and supporting documents actually say.

**Out of scope:** Sector-specific regulation outside AI/data protection (e.g., specific HR-tech licensing rules, medical device regulation), older deprecated regulation, customer-side documentation. The corpus is deliberately bounded to the EU AI Act, UK/EU GDPR, ICO AI guidance, and the Novara fictive bundle.

## 2. Corpus structure

```
corpus/
├── manifest.json                                         (auto-generated; provenance + hashes)
├── regulation/                                           (REG)
│   ├── eu-ai-act-2024-1689.pdf                          (full Regulation EU 2024/1689)
│   ├── eu-ai-act-2024-1689.txt                          (extracted text)
│   ├── uk-gdpr-articles-relevant.txt                    (consolidated cluster: Arts 5, 6, 9, 13, 14, 22, 28, 35)
│   └── uk-gdpr-art-{N}.txt                              (individual articles for chunking)
├── operational/                                          (OPS)
│   └── ico-ai-guidance/
│       ├── 01-about.txt
│       ├── 02-accountability-governance.txt
│       ├── 03-transparency.txt
│       ├── 04-lawfulness.txt
│       ├── 05-accuracy.txt
│       ├── 06-fairness.txt
│       ├── 07-individual-rights.txt
│       ├── 08-security-data-minimisation.txt
│       └── 09-article-22-fairness.txt                   (special focus chapter)
├── deployer/                                             (DEP — Novara core policy)
│   ├── novara-ai-policy-v3.1.pdf
│   └── novara-ai-policy-v3.1.txt                        (extracted text)
└── deployer-extras/                                      (DEP — Novara supporting documents)
    ├── novara-talentlens-model-card.md
    ├── novara-talentlens-dpia.md
    ├── novara-talentlens-transparency-notice.md
    ├── novara-2025-annual-ai-governance-report.md
    └── novara-model-intake-assessment-template-talentlens.md
```

Each text file is the canonical retrieval source. Original PDF/HTML files stay in the corpus folder for citation provenance and for the report's appendix (the marker may want to verify cited content against original sources).

## 3. Per-bucket content list with sources

### 3.1 Regulation bucket

**EU AI Act — Regulation (EU) 2024/1689**

Primary source: [EUR-Lex official PDF](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689). Note that EUR-Lex sometimes returns HTTP 202 with empty body during initial fetch attempts — if that happens, fall back to the EU Council version (PE-CONS 24/24, available via [eur-lex.europa.eu/eli/reg/2024/1689/oj/eng](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng)) which is textually identical.

For chunking, the full 419-page Act is more than the system needs. Daria can either ingest the full text (preferable for completeness) or extract just the articles relevant to the project's scope. The relevant cluster is:

- **Article 3** (definitions, including "deployer", "provider", "high-risk AI system")
- **Article 5** (prohibited AI practices — relevant to ensure Novara products don't fall here)
- **Article 6** (classification rules for high-risk AI systems)
- **Article 10** (training, validation, testing data quality)
- **Article 13** (instructions for use to deployers)
- **Article 14** (human oversight)
- **Article 26** (deployer obligations — DPIAs, log retention, worker information)
- **Article 27** (fundamental rights impact assessment)
- **Article 50** (transparency obligations)
- **Annex III** (high-risk AI categories), specifically:
  - §3 (Education and vocational training)
  - §4 (Employment, workers management) — primary for TalentLens
  - §5 (Access to essential services — credit, insurance)

Extraction: use `pdftotext` or `pdfplumber`. The output `.txt` should be cleaned of page furniture lines (`PE-CONS 24/24    AD/DOS/di    196   TREE.2.B    EN`-style headers) but Daria can do this lightly — perfect cleaning isn't necessary; the chunker can absorb some noise.

**UK/EU GDPR — Selected articles**

UK GDPR articles share numbering and substantive text with EU GDPR for the cluster used here. Source: [gdpr-info.eu](https://gdpr-info.eu/) per article. UK-specific implementation differences are noted in the Data Protection Act 2018 (`legislation.gov.uk/ukpga/2018/12/contents`) — for this project, the EU GDPR text is sufficient since the Novara scenario doesn't hinge on UK-specific derogations.

Articles to include:

- **Article 5** (principles: lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity & confidentiality, accountability)
- **Article 6** (lawfulness of processing)
- **Article 9** (special category data — relevant if TalentLens ingests CVs containing health/disability/race/etc.)
- **Article 13** (information when personal data collected from data subject)
- **Article 14** (information when personal data not collected from data subject)
- **Article 22** (automated decisions — paradigmatic for TalentLens)
- **Article 28** (processor obligations)
- **Article 35** (data protection impact assessment)

Provide both per-article files (for granular chunking) and a single consolidated file (for systems that prefer larger context).

### 3.2 Operational guidance bucket

**ICO Guidance on AI and data protection**

Source: [ICO main AI guidance suite](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/). Multiple chapters; each becomes its own file in the corpus.

Chapters to include:
- About this guidance
- Accountability and governance implications of AI
- How do we ensure transparency in AI?
- How do we ensure lawfulness in AI?
- What do we need to know about accuracy and statistical accuracy?
- How do we ensure fairness in AI?
- How do we ensure individual rights in our AI systems?
- How should we assess security and data minimisation in AI?
- What is the impact of Article 22 of the UK GDPR on fairness? (special focus)

Each chapter is fetched as HTML, then extracted to plain text. Strip the standard ICO preamble that appears at the start of every page ("Artificial intelligence Download options...") plus footer navigation.

**Optional additions if time permits:**
- ICO AI and Data Protection Risk Toolkit (XLSX) — 91 rows of structured risk statements, useful for retrieval but requires special handling (each row becomes its own chunk)
- ICO response to the consultation series on generative AI (December 2024) — six chapters, particularly relevant for foundation-model controllership questions
- ICO Explaining Decisions Made with AI (with Alan Turing Institute) — overview plus three Parts

These are valuable extensions but not essential for the core gap analysis. Recommendation: include the main guidance chapters only in the v1 corpus; add the others if Daria has corpus capacity remaining.

### 3.3 Deployer (Novara core policy)

**Source:** the existing `novara_ai_policy_v3.1.pdf` already in the project workspace.

**Extraction:** `pdftotext` to produce `novara-ai-policy-v3.1.txt`. This 15-page document is the central object of the gap analysis system. Every gap-analysis query will pull chunks from here.

The policy is structured into ten numbered sections plus two appendices. The chunker should respect this structure — section-level chunks are appropriate. Critical sections:

- §3 AI Product Development Standards (model selection, training data, evaluation gates, red-teaming, HITL)
- §4 Privacy and Data Protection (legal basis, retention, data subject rights, cross-border transfers)
- §5 AI Governance Structure (governance roles, risk register, incident response, external audits)
- §6 Responsible AI Principles
- Appendix A — High-Risk AI Feature Criteria (the self-classification logic)

### 3.4 Deployer-extras (Novara supporting documents)

To be drafted by Daria per `v2_supporting_documents_brief.md`. Five fictive supporting documents grounded in real-world templates:

- **TalentLens Model Card** (4–6 pages) — product description, training data, evaluation metrics, fairness analysis, known limitations, deployment recommendations
- **TalentLens DPIA** (5–8 pages) — processing description, necessity & proportionality, risks identified, mitigations, residual risks
- **TalentLens Transparency Notice** (2–3 pages) — what candidates are told when assessed by the AI
- **2025 Annual AI Governance Report** (3–5 pages) — executive summary of risk register, audit findings, regulatory monitoring updates
- **Model Intake Assessment for TalentLens** (2–3 pages) — filled-in copy of the template referenced in policy §3.1 (NAI-TMPL-0031)

Total fictive supporting corpus: approximately 20–25 pages.

## 4. Corpus size and retrieval characteristics

| Bucket | Approximate file count | Approximate word count |
|---|---|---|
| Regulation | 9 files | 90,000–100,000 |
| Operational | 9 files | 50,000–60,000 |
| Deployer (Novara core) | 1 file | 4,000–5,000 |
| Deployer-extras | 5 files | 8,000–12,000 |
| **Total** | **24 files** | **~155,000–175,000 words** |

After chunking (paragraph-level for legal text, sentence-clusters for prose, row-level for ICO Risk Toolkit if included), expect approximately 3,000–5,000 chunks. This is well within in-memory NumPy retrieval capacity (cosine similarity over a 5,000 × 384 matrix is sub-millisecond).

## 5. Chunking strategy (high-level — implementation in `v2_implementation_plan.md`)

The chunker should produce chunks with these properties:

- **Coherence**: each chunk is a coherent unit of meaning — one Article paragraph, one section sub-section, one risk-toolkit row
- **Size**: between 200 and 800 tokens (smaller for retrieval precision, larger for context preservation)
- **Metadata**: every chunk carries `corpus_tag`, `document_id`, `section_reference`, `source_url`, `chunk_id`, and the chunk text

Per-bucket boundaries:

- **AI Act**: split at Article boundary; sub-split at numbered paragraph if Article > 800 tokens
- **GDPR articles**: typically each article fits one chunk; for Article 5, split at principle level
- **ICO chapters**: split at H2/H3 headings within each chapter
- **Novara policy**: split at section boundary (§3, §4, §5, etc.); sub-split at sub-section if needed
- **Novara extras**: split at named-section boundaries within each document

This is structure-aware splitting — not character-count splitting. The structure carries meaning and the system needs to retrieve at appropriate granularity for citation accuracy.

## 6. Manifest and provenance

A `manifest.json` is generated automatically as part of corpus loading. For each file:

```json
{
  "path": "regulation/eu-ai-act-2024-1689.txt",
  "corpus_tag": "REG",
  "document_id": "eu-ai-act-2024-1689",
  "document_title": "Regulation (EU) 2024/1689 — Artificial Intelligence Act",
  "source_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689",
  "doc_pub_date": "2024-07-12",
  "fetch_date": "2026-05-02",
  "size_bytes": 740312,
  "word_count": 93565,
  "sha256": "<full-hash>"
}
```

The manifest lives in the corpus root and is regenerated whenever corpus content changes. It serves three purposes: reproducibility (anyone with the manifest can reconstruct the corpus state), integrity (hashes detect accidental modification), and report appendix material (the marker may want this for the reproducibility dimension of the rubric).

## 7. Refresh policy

The corpus is **frozen** once Daria's build starts. This is critical for evaluation reproducibility. If a regulation amendment, ICO guidance update, or new Novara policy version becomes available mid-project, the response is:

1. **Continue with the frozen v1 corpus.** Note the update in the report's "limitations" section.
2. **Do not modify files in place.** Hashes diverge; integrity checks fail; evaluation results become irreproducible.
3. **For corpus changes warranted by mid-project re-scoping**, create a new versioned snapshot (`corpus-v2/`) with full re-fetch and re-validation; never edit the existing corpus.

For the project's submission, the corpus version used is documented in the report's methodology section. The marker reading the report should be able to identify the exact corpus state results were computed against.

## 8. Validation checks before build starts

Before Daria begins implementation in week 2, the corpus should pass these checks:

- [ ] All files present per the file layout in §2
- [ ] Each text file is non-empty and at least 90% of expected word count (sanity check against extraction failure)
- [ ] Each file's `manifest.json` entry contains all required fields
- [ ] SHA-256 hashes regenerable and match the recorded values
- [ ] Spot-check: open three random regulation chunks, three random operational chunks, three random Novara chunks; confirm they're substantive content, not navigation cruft

A simple validation script (~50 lines of Python) produces a check report. This becomes part of the report appendix as evidence of methodological rigour.

## 9. The deployer-extras drafting workflow

Drafting the five Novara supporting documents is week-1 work for Daria. Recommended approach:

1. Read `v2_supporting_documents_brief.md` to understand each document's purpose, structure, and intentional gaps.
2. For each document, write a first draft using LLM assistance (e.g., Claude or ChatGPT) — use the brief as the prompt, with public templates from real companies as style guidance.
3. Read each draft critically; verify it contains the *intentional gaps* that make the gap-analysis system interesting.
4. Save as `.md` files in `deployer-extras/` per the file layout.
5. Add manifest entries.

Total time estimate: 8–12 hours across the five documents. Each individual document is short (2–8 pages of fictive text); the work is in maintaining consistency with Novara v3.1 and engineering plausible gaps.

## 10. What's deliberately not in the corpus

Documented for the report's "scope and limitations" discussion:

*UK Data Protection Act 2018*. Could be included; for the EU-focused Novara scenario, EU GDPR is sufficient. Including DPA 2018 would add UK-specific complexity (UK GDPR derogations) that the project doesn't need.

*Data (Use and Access) Act 2025*. Recently in force; affects archiving and research provisions but less central to AI deployment compliance. Could be added as future work.

*UK pro-innovation AI White Paper*. Principles-based UK approach; relevant context but not yet operationally binding on Novara, so excluded.

*Sector-specific regulation* (e.g., financial services AI guidance from FCA, medical AI from MHRA). Out of scope — the project is about cross-cutting AI Act + GDPR compliance.

*Customer-side documentation* (e.g., what Novara's customers must do). Out of scope — the project is about Novara's compliance posture, not its customers'.

*Real corporate AI policies* (Microsoft, IBM, etc.). Out of scope — Novara is fictive by design, and real corporate documents would muddy the gap-analysis evaluation by introducing unknown real-world gaps.

— *Corpus specification v2 prepared 2 May 2026. Feeds into `v2_implementation_plan.md` (corpus loading) and `v2_supporting_documents_brief.md` (Novara extras drafting).*
