"""LLM-06 — disk response cache.

Cache keyed on `sha256(model_id::rendered_prompt)` so different models
never pollute each other's cached outputs and eval-phase replay is
deterministic.

Serves four purposes:

  - Rate-limit safety (cache hits don't burn API quota)
  - Dev iteration speed (cache hits are sub-second)
  - Demo pre-warming (planned demo queries are pre-warmed; demo
    latency is sub-second under any backend)
  - Evaluation reproducibility (eval-phase replay against the same
    model produces identical cached outputs)

Cache lives at `llm_cache/` (gitignored). Re-running the chain against
the same query + same model hits the cache and bypasses both the
network and the LLM completely.

Note: Opus (gold-set bootstrap script in eval phase) is NOT routed
through this cache — it's a one-off script outside the FLEX-6
abstraction.

Reference: compliance-gap-analysis-spec.md § LLM-06.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


class DiskCache:
    """Disk-backed response cache keyed on (model_id, rendered_prompt)."""

    def __init__(self, cache_dir: Path | str = Path("llm_cache")) -> None:
        self._dir = Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._file = self._dir / "cache.json"
        if self._file.exists():
            try:
                self._data = json.loads(self._file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                # Corrupted cache file: start fresh rather than crash.
                self._data = {}
        else:
            self._data = {}

    @staticmethod
    def _key(prompt: str, model_id: str) -> str:
        # `model_id` first so the namespace is visible at the start of
        # the hash input; the hash itself collapses both into 64 hex
        # chars but the prefix order matters if we ever debug raw input.
        return hashlib.sha256(
            f"{model_id}::{prompt}".encode("utf-8")
        ).hexdigest()

    def get(self, prompt: str, model_id: str) -> str | None:
        return self._data.get(self._key(prompt, model_id))

    def set(self, prompt: str, model_id: str, response: str) -> None:
        self._data[self._key(prompt, model_id)] = response
        self._file.write_text(
            json.dumps(self._data, indent=2), encoding="utf-8"
        )

    def __len__(self) -> int:
        return len(self._data)
