"""ING-01 unit + integration tests."""

from __future__ import annotations

import time
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.ingestion import (
    Chunk,
    _chunk_id,
    _derive_corpus_tag,
    _derive_document_id,
    _derive_section_reference,
    load_corpus,
)


# --- Unit tests (no I/O) -------------------------------------------------


@pytest.mark.parametrize("path,expected", [
    ("regulation/uk-gdpr-art-22.txt", "REG"),
    ("regulation/eu-ai-act-2024-1689.txt", "REG"),
    ("operational/ico-main-guidance/01-about.txt", "OPS"),
    ("operational/ico-audit-framework/10-human-review.txt", "OPS"),
    ("deployer/novara-ai-policy-v3.1.txt", "DEP"),
    ("deployer-extras/novara-talentlens-dpia.md", "DEP_EXTRAS"),
])
def test_derive_corpus_tag_for_each_bucket(path: str, expected: str) -> None:
    assert _derive_corpus_tag(path) == expected


def test_derive_corpus_tag_rejects_unknown_bucket() -> None:
    with pytest.raises(ValueError):
        _derive_corpus_tag("unknown/some-file.txt")


def test_derive_document_id_strips_extension() -> None:
    assert _derive_document_id("regulation/uk-gdpr-art-22.txt") == "uk-gdpr-art-22"
    assert _derive_document_id("deployer-extras/novara-talentlens-dpia.md") == "novara-talentlens-dpia"
    # Multi-dot filename: Path.stem returns text before the LAST dot.
    assert _derive_document_id("deployer/novara-ai-policy-v3.1.txt") == "novara-ai-policy-v3.1"


@pytest.mark.parametrize("path,expected", [
    ("regulation/uk-gdpr-art-22.txt", "UK GDPR Article 22"),
    ("regulation/uk-gdpr-art-5.txt", "UK GDPR Article 5"),
    ("regulation/uk-gdpr-articles-relevant.txt", "UK GDPR (consolidated relevant articles)"),
    ("regulation/eu-ai-act-2024-1689.txt", "EU AI Act (Regulation 2024/1689)"),
    ("operational/ico-main-guidance/01-about.txt", "ICO Main Guidance — About"),
    ("operational/ico-main-guidance/07-article-22-fairness.txt", "ICO Main Guidance — Article 22 fairness"),
    ("operational/ico-genai-consultation/01-executive-summary.txt", "ICO GenAI Consultation — Executive summary"),
    ("operational/ico-audit-framework/10-human-review.txt", "ICO Audit Framework — Human review"),
    ("deployer/novara-ai-policy-v3.1.txt", "Novara AI Policy v3.1"),
    ("deployer-extras/novara-talentlens-dpia.md", "Novara TalentLens DPIA"),
])
def test_derive_section_reference_table(path: str, expected: str) -> None:
    assert _derive_section_reference(path) == expected


def test_chunk_id_is_deterministic() -> None:
    assert _chunk_id("regulation/uk-gdpr-art-22.txt") == _chunk_id("regulation/uk-gdpr-art-22.txt")


def test_chunk_id_strips_extension() -> None:
    assert _chunk_id("regulation/uk-gdpr-art-22.txt") == "regulation/uk-gdpr-art-22"
    assert _chunk_id("deployer-extras/novara-talentlens-dpia.md") == "deployer-extras/novara-talentlens-dpia"


def test_chunk_id_distinguishes_same_stem_in_different_subfolders() -> None:
    # Real corpus collision: ico-main-guidance/03-transparency.txt and
    # ico-audit-framework/03-transparency.txt — same stem, same OPS tag.
    a = _chunk_id("operational/ico-main-guidance/03-transparency.txt")
    b = _chunk_id("operational/ico-audit-framework/03-transparency.txt")
    assert a != b


def test_chunk_dataclass_is_frozen() -> None:
    chunk = Chunk(
        chunk_id="REG:x",
        corpus_tag="REG",
        document_id="x",
        section_reference="X",
        source_url="",
        chunk_text="content",
        file_path="regulation/x.txt",
        sha256_short="abc",
    )
    with pytest.raises(FrozenInstanceError):
        chunk.chunk_text = "different"  # type: ignore[misc]


# --- Integration tests (against the real frozen corpus) -----------------


def test_load_corpus_returns_42_chunks(corpus_manifest_path: Path) -> None:
    # 44 manifest entries minus 2 PDFs (word_count == 0).
    chunks = load_corpus(corpus_manifest_path)
    assert len(chunks) == 42


def test_every_chunk_has_required_fields_populated(corpus_manifest_path: Path) -> None:
    chunks = load_corpus(corpus_manifest_path)
    for c in chunks:
        assert c.chunk_id, f"empty chunk_id: {c.file_path}"
        assert c.corpus_tag, f"empty corpus_tag: {c.file_path}"
        assert c.document_id, f"empty document_id: {c.file_path}"
        assert c.section_reference, f"empty section_reference: {c.file_path}"
        # source_url may be a non-URL string for fictive Novara files
        # (manifest records "— Fictive (Novara fabricated for project) —"),
        # so assert presence-of-string, not URL shape.
        assert isinstance(c.source_url, str) and c.source_url, f"empty source_url: {c.file_path}"
        assert c.chunk_text, f"empty chunk_text: {c.file_path}"
        assert c.file_path, "empty file_path"
        assert c.sha256_short, f"empty sha256_short: {c.file_path}"


def test_every_chunk_has_one_of_four_corpus_tags(corpus_manifest_path: Path) -> None:
    chunks = load_corpus(corpus_manifest_path)
    valid = {"REG", "OPS", "DEP", "DEP_EXTRAS"}
    for c in chunks:
        assert c.corpus_tag in valid, f"unexpected tag {c.corpus_tag} on {c.file_path}"


def test_corpus_tag_distribution(corpus_manifest_path: Path) -> None:
    chunks = load_corpus(corpus_manifest_path)
    counts: dict[str, int] = {}
    for c in chunks:
        counts[c.corpus_tag] = counts.get(c.corpus_tag, 0) + 1
    # Post-PR2 corpus, PDFs excluded:
    #   regulation: 1 ai-act .txt + 8 GDPR articles + 1 consolidated = 10
    #   operational: 10 main + 6 genai + 10 audit = 26
    #   deployer: 1 (PDF excluded)
    #   deployer-extras: 5
    assert counts == {"REG": 10, "OPS": 26, "DEP": 1, "DEP_EXTRAS": 5}


def test_chunk_ids_are_unique_across_corpus(corpus_manifest_path: Path) -> None:
    chunks = load_corpus(corpus_manifest_path)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_load_corpus_is_idempotent(corpus_manifest_path: Path) -> None:
    a = load_corpus(corpus_manifest_path)
    b = load_corpus(corpus_manifest_path)
    assert [c.chunk_id for c in a] == [c.chunk_id for c in b]
    assert [c.chunk_text for c in a] == [c.chunk_text for c in b]


def test_chunk_text_meets_minimum_word_floor(corpus_manifest_path: Path) -> None:
    # Lower bound chosen below the smallest real file (audit-framework
    # overview at 96 words). Guards against accidental loading of empty
    # or truncated content.
    chunks = load_corpus(corpus_manifest_path)
    for c in chunks:
        assert len(c.chunk_text.split()) >= 50, f"too few words: {c.file_path}"


def test_load_corpus_completes_in_under_60s(corpus_manifest_path: Path) -> None:
    start = time.perf_counter()
    chunks = load_corpus(corpus_manifest_path)
    elapsed = time.perf_counter() - start
    assert elapsed < 60.0, f"took {elapsed:.2f}s"
    assert len(chunks) > 0
