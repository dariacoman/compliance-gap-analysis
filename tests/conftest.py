from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "live_api: tests that hit a real external API. Skipped by default; "
        "run with `pytest -m live_api` to opt in.",
    )


def pytest_collection_modifyitems(config, items):
    """Auto-skip `live_api` tests unless explicitly opted in via -m live_api."""
    selected = config.getoption("-m") or ""
    if "live_api" in selected:
        return
    skip_marker = pytest.mark.skip(
        reason="live API test (use `pytest -m live_api` to enable)"
    )
    for item in items:
        if "live_api" in item.keywords:
            item.add_marker(skip_marker)


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


@pytest.fixture(scope="session")
def corpus_retriever(corpus_chunks, corpus_embeddings):
    """RET-01 retriever wired against the real corpus + embeddings."""
    from src.ingestion import _get_st_model
    from src.retrieval import ChunkEmbeddingRetriever
    embeddings, chunk_ids = corpus_embeddings
    model = _get_st_model("multi-qa-MiniLM-L6-cos-v1")
    return ChunkEmbeddingRetriever(corpus_chunks, embeddings, chunk_ids, model)
