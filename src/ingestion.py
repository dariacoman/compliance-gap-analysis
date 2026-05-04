"""ING-01, ING-02, ING-03 — corpus ingestion.

Loads the four-bucket corpus (regulation, ICO operational guidance,
Novara deployer policy, Novara deployer-extras) into typed chunk
records (ING-01); chunks legal texts at Article/§ boundaries with
sentence segmentation within larger units (ING-02); embeds chunks
with `multi-qa-MiniLM-L6-cos-v1` and caches them on disk (ING-03).

Pre-conditions: `corpus/manifest.json` complete, hashes verified
(`scripts/validate_corpus.py` passes).

Outputs: typed chunk records carrying corpus_tag, document_id,
section_reference, source_url, chunk_id, chunk_text, plus an
on-disk embedding cache under `embeddings/`.

Reference: compliance-gap-analysis-spec.md § Group: Ingestion.
AI Act extraction observations: docs/ai-act-extraction-notes.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CORPUS_TAGS = ("REG", "OPS", "DEP", "DEP_EXTRAS")

_STATIC_LABELS: dict[str, str] = {
    "regulation/uk-gdpr-articles-relevant.txt": "UK GDPR (consolidated relevant articles)",
    "regulation/eu-ai-act-2024-1689.txt": "EU AI Act (Regulation 2024/1689)",
    "deployer/novara-ai-policy-v3.1.txt": "Novara AI Policy v3.1",
    "deployer-extras/novara-talentlens-dpia.md": "Novara TalentLens DPIA",
    "deployer-extras/novara-talentlens-model-card.md": "Novara TalentLens Model Card",
    "deployer-extras/novara-talentlens-transparency-notice.md": "Novara TalentLens Transparency Notice",
    "deployer-extras/novara-talentlens-model-intake-assessment.md": "Novara TalentLens Model Intake Assessment",
    "deployer-extras/novara-2025-ai-governance-report.md": "Novara 2025 AI Governance Report",
}

_OPS_SUB_LABELS: dict[str, str] = {
    "ico-main-guidance": "ICO Main Guidance",
    "ico-genai-consultation": "ICO GenAI Consultation",
    "ico-audit-framework": "ICO Audit Framework",
}


@dataclass(frozen=True, slots=True)
class Chunk:
    chunk_id: str
    corpus_tag: str
    document_id: str
    section_reference: str
    source_url: str
    chunk_text: str
    file_path: str
    sha256_short: str


def _derive_corpus_tag(file_path: str) -> str:
    if file_path.startswith("regulation/"):
        return "REG"
    if file_path.startswith("operational/"):
        return "OPS"
    if file_path.startswith("deployer-extras/"):
        return "DEP_EXTRAS"
    if file_path.startswith("deployer/"):
        return "DEP"
    raise ValueError(f"unknown bucket for path: {file_path}")


def _derive_document_id(file_path: str) -> str:
    return Path(file_path).stem


def _derive_section_reference(file_path: str) -> str:
    if file_path in _STATIC_LABELS:
        return _STATIC_LABELS[file_path]

    parts = Path(file_path).parts
    stem = Path(file_path).stem

    # regulation/uk-gdpr-art-{N}.txt -> "UK GDPR Article {N}"
    if stem.startswith("uk-gdpr-art-"):
        return f"UK GDPR Article {stem.removeprefix('uk-gdpr-art-')}"

    # operational/{sub}/{NN-slug}.txt -> "{Sub label} — {Title}"
    if parts[0] == "operational" and len(parts) == 3:
        sub_label = _OPS_SUB_LABELS.get(parts[1], parts[1])
        head, _, tail = stem.partition("-")
        slug = tail if head.isdigit() and tail else stem
        title = slug.replace("-", " ").capitalize()
        return f"{sub_label} — {title}"

    # Fallback: stem with hyphens turned to spaces, title-cased.
    return stem.replace("-", " ").title()


def _chunk_id(file_path: str) -> str:
    # Path with extension stripped. Globally unique (corpus paths are
    # unique). Initial design used "{corpus_tag}:{document_id}" but that
    # collided across OPS sub-folders (e.g., ico-main-guidance and
    # ico-audit-framework both have a 03-transparency.txt with the same
    # stem). Path-based IDs sidestep the collision and stay readable.
    return str(Path(file_path).with_suffix(""))


def load_corpus(manifest_path: Path = Path("corpus/manifest.json")) -> list[Chunk]:
    """Load every text file in the manifest into a Chunk record.

    Skips manifest entries with `word_count == 0` (PDFs whose .txt
    siblings are the canonical retrieval source per v2 corpus spec § 2).
    Returns chunks in manifest order; chunk_ids are stable across re-runs
    against the same manifest.
    """
    corpus_root = manifest_path.parent
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))

    chunks: list[Chunk] = []
    for entry in entries:
        if entry["word_count"] == 0:
            # PDF entries are present for citation provenance only;
            # their .txt siblings are the canonical retrieval source.
            continue

        rel_path = entry["path"]
        text = (corpus_root / rel_path).read_text(encoding="utf-8")
        corpus_tag = _derive_corpus_tag(rel_path)
        document_id = _derive_document_id(rel_path)

        chunks.append(Chunk(
            chunk_id=_chunk_id(rel_path),
            corpus_tag=corpus_tag,
            document_id=document_id,
            section_reference=_derive_section_reference(rel_path),
            source_url=entry["source_url"],
            chunk_text=text,
            file_path=rel_path,
            sha256_short=entry["sha256_short"],
        ))

    return chunks
