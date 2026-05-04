from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def corpus_manifest_path() -> Path:
    return PROJECT_ROOT / "corpus" / "manifest.json"


@pytest.fixture(scope="session")
def corpus_documents(corpus_manifest_path):
    """Loaded Documents (ING-01) — shared across ING-02 integration tests."""
    from src.ingestion import load_corpus
    return load_corpus(corpus_manifest_path)


@pytest.fixture(scope="session")
def corpus_chunks(corpus_documents):
    """Refined Chunks (ING-02) — shared across integration tests."""
    from src.ingestion import chunk_corpus
    return chunk_corpus(corpus_documents)


@pytest.fixture(scope="session")
def corpus_embeddings(corpus_chunks, tmp_path_factory):
    """Embedded corpus (ING-03) — shared. Uses a tmp cache dir so test
    runs don't pollute the project's embeddings/."""
    from src.ingestion import embed_chunks
    cache_dir = tmp_path_factory.mktemp("ing03_cache")
    return embed_chunks(corpus_chunks, cache_dir=cache_dir)
