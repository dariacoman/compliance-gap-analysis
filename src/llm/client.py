"""LLM-01 — abstract LLMClient interface.

The model-blind interface that all chain code types against. Three
properties (`model_family`, `model_id`, `max_context`) and one
abstract method (`_complete(prompt) -> str`).

This is the type that chain variables must be annotated against —
never against `RoutingClient` (LLM-05) and never against a concrete
per-model adapter (LLM-03). Mocks in tests must implement this ABC,
not subclass routing or adapters.

The discipline is what makes FLEX-6 strip-safe: as long as chain
code types against the ABC, the routing layer is swap-out-able for
any concrete adapter. tests/test_typing.py mechanically validates
this (LLM-08).

Reference: compliance-gap-analysis-spec.md § LLM-01.
"""

from __future__ import annotations

import abc
from typing import Any


class LLMClient(abc.ABC):
    """Model-blind interface; the only type chain code annotates against."""

    @property
    @abc.abstractmethod
    def model_family(self) -> str:
        """e.g. 'llama' or 'gemma' — used for prompt-registry keying."""

    @property
    @abc.abstractmethod
    def model_id(self) -> str:
        """Stable model identifier — used for cache keying."""

    @property
    @abc.abstractmethod
    def max_context(self) -> int:
        """Token budget — used for token-guard checks (CHN-04)."""

    @abc.abstractmethod
    def _complete(self, prompt: str) -> str:
        """Single uncached completion call."""

    @abc.abstractmethod
    def decompose_query(
        self, query: str, *, max_sub_questions: int = 4
    ) -> list[str]:
        """CHN-01 — return a list of focused sub-questions."""

    @abc.abstractmethod
    def extract_obligations(
        self, sub_question: str, regulation_chunks: list[Any]
    ) -> list[str]:
        """CHN-03 — return up to 5 atomic obligations from the chunks."""

    @abc.abstractmethod
    def classify_obligations(
        self,
        sub_question: str,
        obligations: list[str],
        evidence: dict[str, list[Any]],
    ) -> list[dict[str, Any]]:
        """CHN-04 phase 2 — batched 4-state classifier with citations."""

    @abc.abstractmethod
    def synthesise_register(
        self, rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """CHN-05 — synthesise the residual-risk register from per-obligation rows."""
