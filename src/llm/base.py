"""LLM-02 — BaseLLMClient with concrete task methods.

Concrete task methods that the chain calls without knowing which
model is behind them:

  - decompose_query        — CHN-01 entry point
  - extract_obligations    — CHN-03 entry point
  - classify_obligations   — CHN-04 phase 2 entry point
  - synthesise_register    — CHN-05 entry point

Each task method looks up its prompt from the registry (LLM-04)
keyed on `(task, family)`, calls `_complete_cached()` (which wraps
`_complete()` with the LLM-06 disk cache), and parses the response
with a best-effort JSON-list extractor.

Concrete-on-base-class shape (rather than abstract on the ABC) is a
deliberate D-008 addendum decision — adapters implement `_complete()`
only and inherit task methods for free.

Reference: compliance-gap-analysis-spec.md § LLM-02.
"""

from __future__ import annotations

import json
from typing import Any

from src.llm.cache import DiskCache
from src.llm.client import LLMClient
from src.llm.prompts import render_prompt


class SchemaParseError(ValueError):
    """Raised when LLM output cannot be parsed into the expected JSON shape.

    Caught by `RoutingClient` (LLM-05) which retries the primary with a
    feedback-augmented prompt once, then falls back to the secondary.
    """


def _parse_json_list(raw: str) -> list[Any]:
    """Best-effort extraction of a JSON list from LLM output.

    Tolerant to leading/trailing prose ("Sure, here's the JSON: [...]")
    and to common markdown code-fence wrappers (```json ... ```). Raises
    `SchemaParseError` if no recoverable JSON list is present.
    """
    if not raw or not raw.strip():
        raise SchemaParseError("empty LLM response")

    # Find the outermost square-bracket span.
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise SchemaParseError(
            f"no JSON list bracket pair found in response: {raw[:200]!r}"
        )

    span = raw[start : end + 1]
    try:
        parsed = json.loads(span)
    except json.JSONDecodeError as exc:
        raise SchemaParseError(
            f"JSON decode failed at offset {exc.pos}: {span[:200]!r}"
        ) from exc
    # By construction `parsed` is whatever sits between the outermost
    # brackets — for valid JSON that's always a list. We assert it
    # explicitly so a malformed schema surfaces as SchemaParseError
    # rather than as an indexing error downstream.
    assert isinstance(parsed, list)
    return parsed


_CHUNK_SNIPPET_LIMIT = 400  # chars per chunk in the prompt — keeps batched
                            # classifier prompts under Groq's 12K TPM ceiling
                            # for the build-phase corpus shape.


def _format_chunks(chunks: list[Any], *, snippet_limit: int = _CHUNK_SNIPPET_LIMIT) -> str:
    """Format retrieved chunks into a prompt-friendly string.

    Each chunk is rendered as `[chunk_id] section_reference: snippet`
    where snippet is at most `snippet_limit` characters. Truncating
    keeps the batched classifier prompt under Groq's TPM cap when many
    chunks are aggregated across obligations.
    """
    lines = []
    for c in chunks:
        cid = getattr(c, "chunk_id", "?")
        section = getattr(c, "section_reference", "")
        text = getattr(c, "chunk_text", "")
        if len(text) > snippet_limit:
            text = text[:snippet_limit] + "…"
        lines.append(f"[{cid}] {section}: {text}")
    return "\n\n".join(lines)


class BaseLLMClient(LLMClient):
    """Concrete task methods; adapters subclass this and implement `_complete`."""

    def __init__(self, *, cache: DiskCache | None = None) -> None:
        self._cache = cache

    def _complete_cached(self, prompt: str) -> str:
        """Cache-aware wrapper around `_complete`."""
        if self._cache is None:
            return self._complete(prompt)
        cached = self._cache.get(prompt, self.model_id)
        if cached is not None:
            return cached
        result = self._complete(prompt)
        self._cache.set(prompt, self.model_id, result)
        return result

    def decompose_query(
        self, query: str, *, max_sub_questions: int = 4
    ) -> list[str]:
        rendered = render_prompt(
            "decompose",
            self.model_family,
            query=query,
            max_sub_questions=max_sub_questions,
        )
        raw = self._complete_cached(rendered)
        sub_questions = _parse_json_list(raw)
        # decisions.md §3 cap.
        return [str(q) for q in sub_questions[:max_sub_questions]]

    def extract_obligations(
        self, sub_question: str, regulation_chunks: list[Any]
    ) -> list[str]:
        rendered = render_prompt(
            "extract",
            self.model_family,
            sub_question=sub_question,
            chunks_text=_format_chunks(regulation_chunks),
        )
        raw = self._complete_cached(rendered)
        # Spec § ING-03: cap at ~5 obligations per sub-question.
        return [str(o) for o in _parse_json_list(raw)[:5]]

    def classify_obligations(
        self,
        sub_question: str,
        obligations: list[str],
        evidence: dict[str, list[Any]],
    ) -> list[dict[str, Any]]:
        rendered = render_prompt(
            "classify",
            self.model_family,
            sub_question=sub_question,
            obligations=json.dumps(obligations, indent=2),
            evidence=json.dumps(
                {k: _format_chunks(v) for k, v in evidence.items()}, indent=2
            ),
        )
        raw = self._complete_cached(rendered)
        return list(_parse_json_list(raw))

    def synthesise_register(
        self, rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        rendered = render_prompt(
            "synthesise",
            self.model_family,
            rows=json.dumps(rows, indent=2, default=str),
        )
        raw = self._complete_cached(rendered)
        return list(_parse_json_list(raw))
