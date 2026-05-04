from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def corpus_manifest_path() -> Path:
    return PROJECT_ROOT / "corpus" / "manifest.json"
