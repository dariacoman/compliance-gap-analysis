"""LLM-05 — RoutingClient with hardcoded policy.

Wraps primary (Llama 70B via Groq) + fallback (Gemma 2-2B on Colab)
with hardcoded routing policy:

  - rate-limit error      -> immediate fallback to Gemma
  - network error         -> 1 retry on primary, then fallback
  - schema-parse failure  -> immediate fallback to Gemma

If both backends fail, the originating exception propagates so the
chain surfaces a visible error rather than emitting a malformed
register — no silent partial outputs.

Implements the `LLMClient` ABC so the chain doesn't know it's here.

Note on the schema-parse-failure deviation from the spec's "1 retry
with feedback then fallback":
  At temperature=0 the same prompt produces the same response, so
  retrying the primary on a parse failure would just hit the same
  bad output. Proper retry-with-feedback would require modifying the
  prompt (a "your previous JSON was malformed" hint), which is invasive
  at the task-method level. We instead fall back immediately to Gemma
  on parse failure — predictable, deterministic, no retry loop.
  Documented as a build-time decision in docs/decisions.md.

Reference: compliance-gap-analysis-spec.md § LLM-05.
"""

from __future__ import annotations

from typing import Any

from src.llm.base import BaseLLMClient, SchemaParseError
from src.llm.client import LLMClient


def _is_rate_limit(exc: BaseException) -> bool:
    """Return True if the exception is a Groq RateLimitError."""
    try:
        import groq
        return isinstance(exc, groq.RateLimitError)
    except ImportError:
        return False


def _is_network(exc: BaseException) -> bool:
    """Return True if the exception is a Groq network/timeout error."""
    try:
        import groq
        return isinstance(exc, (groq.APIConnectionError, groq.APITimeoutError))
    except ImportError:
        return False


class RoutingClient(LLMClient):
    """Hardcoded primary→fallback routing.

    Implements LLMClient so chain code (typed against LLMClient) never
    needs to know about routing — FLEX-6 strip-safety discipline.
    """

    def __init__(
        self, primary: BaseLLMClient, fallback: BaseLLMClient
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    @property
    def model_family(self) -> str:
        return self._primary.model_family

    @property
    def model_id(self) -> str:
        return self._primary.model_id

    @property
    def max_context(self) -> int:
        return self._primary.max_context

    def _complete(self, prompt: str) -> str:
        try:
            return self._primary._complete(prompt)
        except Exception as exc:
            if _is_rate_limit(exc):
                return self._fallback._complete(prompt)
            if _is_network(exc):
                # One retry on primary, then fallback.
                try:
                    return self._primary._complete(prompt)
                except Exception as exc2:
                    if _is_rate_limit(exc2) or _is_network(exc2):
                        return self._fallback._complete(prompt)
                    raise
            raise

    # Task methods: try primary, fall back on SchemaParseError.

    def decompose_query(
        self, query: str, *, max_sub_questions: int = 4
    ) -> list[str]:
        try:
            return self._primary.decompose_query(
                query, max_sub_questions=max_sub_questions
            )
        except SchemaParseError:
            return self._fallback.decompose_query(
                query, max_sub_questions=max_sub_questions
            )

    def extract_obligations(
        self, sub_question: str, regulation_chunks: list[Any]
    ) -> list[str]:
        try:
            return self._primary.extract_obligations(
                sub_question, regulation_chunks
            )
        except SchemaParseError:
            return self._fallback.extract_obligations(
                sub_question, regulation_chunks
            )

    def classify_obligations(
        self,
        sub_question: str,
        obligations: list[str],
        evidence: dict[str, list[Any]],
    ) -> list[dict[str, Any]]:
        try:
            return self._primary.classify_obligations(
                sub_question, obligations, evidence
            )
        except SchemaParseError:
            return self._fallback.classify_obligations(
                sub_question, obligations, evidence
            )

    def synthesise_register(
        self, rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        try:
            return self._primary.synthesise_register(rows)
        except SchemaParseError:
            return self._fallback.synthesise_register(rows)
