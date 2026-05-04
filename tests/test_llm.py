"""LLM cluster (LLM-01..06) unit + integration tests.

Live API call lives in a single test marked `@pytest.mark.live_api`;
default `pytest tests/` skips it. Run with `pytest -m live_api` to
exercise it explicitly.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.llm.base import BaseLLMClient, SchemaParseError, _parse_json_list, _format_chunks
from src.llm.cache import DiskCache
from src.llm.client import LLMClient
from src.llm.prompts import PROMPTS, render_prompt


# === LLM-01 — LLMClient ABC ==============================================


def test_llmclient_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        LLMClient()  # type: ignore[abstract]


def test_subclass_missing_abstract_method_cannot_instantiate() -> None:
    class Incomplete(LLMClient):
        # Missing model_family, _complete, etc.
        @property
        def model_id(self) -> str:
            return "x"

    with pytest.raises(TypeError):
        Incomplete()  # type: ignore[abstract]


def test_complete_subclass_can_instantiate() -> None:
    class Complete(LLMClient):
        @property
        def model_family(self) -> str:
            return "test"

        @property
        def model_id(self) -> str:
            return "test-1"

        @property
        def max_context(self) -> int:
            return 1024

        def _complete(self, prompt: str) -> str:
            return "ok"

        def decompose_query(self, query, *, max_sub_questions=4):
            return []

        def extract_obligations(self, sub_question, regulation_chunks):
            return []

        def classify_obligations(self, sub_question, obligations, evidence):
            return []

        def synthesise_register(self, rows):
            return []

    c = Complete()
    assert c.model_family == "test"
    assert c.max_context == 1024


# === LLM-04 — Prompt registry ============================================


def test_all_eight_task_family_keys_present() -> None:
    expected_tasks = {"decompose", "extract", "classify", "synthesise"}
    expected_families = {"llama", "gemma"}
    expected = {(t, f) for t in expected_tasks for f in expected_families}
    assert set(PROMPTS.keys()) == expected


def test_every_prompt_template_mentions_json() -> None:
    for key, template in PROMPTS.items():
        assert "JSON" in template or "json" in template, (
            f"prompt {key} missing JSON output instruction"
        )


def test_render_prompt_substitutes_kwargs() -> None:
    rendered = render_prompt(
        "decompose", "llama", query="Article 22 compliance", max_sub_questions=2
    )
    assert "Article 22 compliance" in rendered
    assert "2" in rendered


def test_render_prompt_unknown_task_raises_keyerror() -> None:
    with pytest.raises(KeyError):
        render_prompt("nonexistent_task", "llama", query="x")


def test_render_prompt_unknown_family_raises_keyerror() -> None:
    with pytest.raises(KeyError):
        render_prompt("decompose", "nonexistent_family", query="x", max_sub_questions=2)


# === LLM-06 — DiskCache ==================================================


def test_diskcache_set_then_get_roundtrip(tmp_path: Path) -> None:
    cache = DiskCache(cache_dir=tmp_path)
    cache.set("hello", "llama-3.3", "world")
    assert cache.get("hello", "llama-3.3") == "world"


def test_diskcache_returns_none_for_unseen_prompt(tmp_path: Path) -> None:
    cache = DiskCache(cache_dir=tmp_path)
    assert cache.get("never seen", "any") is None


def test_diskcache_persists_across_instances(tmp_path: Path) -> None:
    a = DiskCache(cache_dir=tmp_path)
    a.set("p1", "m1", "r1")
    # Fresh instance, same dir.
    b = DiskCache(cache_dir=tmp_path)
    assert b.get("p1", "m1") == "r1"


def test_diskcache_key_includes_model_id(tmp_path: Path) -> None:
    cache = DiskCache(cache_dir=tmp_path)
    cache.set("same prompt", "model-a", "response-a")
    cache.set("same prompt", "model-b", "response-b")
    assert cache.get("same prompt", "model-a") == "response-a"
    assert cache.get("same prompt", "model-b") == "response-b"


def test_diskcache_file_is_valid_json(tmp_path: Path) -> None:
    cache = DiskCache(cache_dir=tmp_path)
    cache.set("p", "m", "r")
    data = json.loads((tmp_path / "cache.json").read_text())
    assert isinstance(data, dict)
    assert len(data) == 1


def test_diskcache_accepts_string_cache_dir(tmp_path: Path) -> None:
    """Common ergonomic case: callers pass a string, not a Path."""
    cache = DiskCache(cache_dir=str(tmp_path))
    cache.set("p", "m", "r")
    assert cache.get("p", "m") == "r"


def test_diskcache_handles_corrupted_file(tmp_path: Path) -> None:
    # Pre-populate a corrupted cache file.
    (tmp_path / "cache.json").write_text("not valid json {{{")
    cache = DiskCache(cache_dir=tmp_path)
    # Should start fresh rather than crash.
    assert cache.get("anything", "any") is None
    cache.set("p", "m", "r")
    assert cache.get("p", "m") == "r"


# === LLM-02 — BaseLLMClient + JSON parsing ===============================


class _StubClient(BaseLLMClient):
    """Test fixture: BaseLLMClient subclass with a programmable `_complete`.

    The stub records every call and returns canned responses set via
    `set_response()`. Used to exercise the cache wrapper, task methods,
    and parsing tolerance without touching a real model.
    """

    def __init__(self, *, family: str = "llama", cache=None):
        super().__init__(cache=cache)
        self._family = family
        self._next_responses: list[str] = []
        self.calls: list[str] = []

    @property
    def model_family(self) -> str:
        return self._family

    @property
    def model_id(self) -> str:
        return f"stub-{self._family}-1"

    @property
    def max_context(self) -> int:
        return 8192

    def queue(self, *responses: str) -> None:
        self._next_responses.extend(responses)

    def _complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        if self._next_responses:
            return self._next_responses.pop(0)
        return "[]"  # safe default — empty JSON list


def test_parse_json_list_pure_json() -> None:
    assert _parse_json_list('["a", "b"]') == ["a", "b"]


def test_parse_json_list_with_preamble() -> None:
    raw = 'Sure, here is the JSON: ["a", "b"] hope this helps.'
    assert _parse_json_list(raw) == ["a", "b"]


def test_parse_json_list_with_code_fence() -> None:
    raw = '```json\n["a", "b"]\n```'
    assert _parse_json_list(raw) == ["a", "b"]


def test_parse_json_list_with_objects() -> None:
    raw = '[{"x": 1}, {"y": 2}]'
    assert _parse_json_list(raw) == [{"x": 1}, {"y": 2}]


def test_parse_json_list_empty_response_raises() -> None:
    with pytest.raises(SchemaParseError, match="empty"):
        _parse_json_list("")


def test_parse_json_list_no_brackets_raises() -> None:
    with pytest.raises(SchemaParseError, match="bracket"):
        _parse_json_list("This is just prose with no JSON.")


def test_parse_json_list_malformed_json_raises() -> None:
    # Has both [ and ] but invalid JSON inside.
    with pytest.raises(SchemaParseError, match="decode"):
        _parse_json_list('[abc not valid json def]')


def test_parse_json_list_no_brackets_in_object_response_raises() -> None:
    # Object-only output with no list brackets falls through to the
    # "no bracket pair" branch — same SchemaParseError class, different
    # message. The downstream contract (SchemaParseError) is what
    # matters; the routing layer doesn't differentiate.
    with pytest.raises(SchemaParseError):
        _parse_json_list('Result: {"key": "value"}')


def test_format_chunks_includes_id_and_section() -> None:
    class _C:
        chunk_id = "abc"
        section_reference = "GDPR Art 22"
        chunk_text = "The data subject..."
    out = _format_chunks([_C(), _C()])
    assert "abc" in out
    assert "GDPR Art 22" in out
    assert "The data subject" in out


def test_complete_cached_hits_cache_on_second_call(tmp_path) -> None:
    cache = DiskCache(cache_dir=tmp_path)
    stub = _StubClient(cache=cache)
    stub.queue("first response")
    a = stub._complete_cached("the prompt")
    b = stub._complete_cached("the prompt")
    assert a == b == "first response"
    assert len(stub.calls) == 1, f"expected 1 _complete call, got {len(stub.calls)}"


def test_complete_cached_with_no_cache_always_calls_complete() -> None:
    stub = _StubClient(cache=None)
    stub.queue("first", "second")
    a = stub._complete_cached("p")
    b = stub._complete_cached("p")
    assert a == "first"
    assert b == "second"
    assert len(stub.calls) == 2


def test_decompose_query_truncates_to_max_sub_questions() -> None:
    stub = _StubClient()
    stub.queue('["q1", "q2", "q3", "q4", "q5", "q6"]')
    out = stub.decompose_query("anything", max_sub_questions=4)
    assert out == ["q1", "q2", "q3", "q4"]


def test_extract_obligations_caps_at_5() -> None:
    stub = _StubClient()
    stub.queue('["o1", "o2", "o3", "o4", "o5", "o6", "o7"]')
    out = stub.extract_obligations("sub", regulation_chunks=[])
    assert len(out) == 5
    assert out == ["o1", "o2", "o3", "o4", "o5"]


def test_classify_obligations_returns_object_list() -> None:
    stub = _StubClient()
    stub.queue('[{"obligation": "o1", "match_status": "silent", "evidence_chunk_ids": []}]')
    out = stub.classify_obligations(
        "sub-question",
        obligations=["o1"],
        evidence={"DEP": [], "DEP_EXTRAS": [], "OPS": []},
    )
    assert out == [
        {"obligation": "o1", "match_status": "silent", "evidence_chunk_ids": []}
    ]


def test_synthesise_register_passes_through_objects() -> None:
    stub = _StubClient()
    stub.queue('[{"row": 1, "gap_characterisation": "missing"}]')
    out = stub.synthesise_register([{"row": 1}])
    assert out == [{"row": 1, "gap_characterisation": "missing"}]


def test_task_methods_uses_correct_family_prompt() -> None:
    stub = _StubClient(family="gemma")
    stub.queue("[]")
    stub.decompose_query("hello", max_sub_questions=2)
    # The captured prompt should match the gemma decompose template
    # (which says "Task: split a compliance query").
    assert "Task: split a compliance query" in stub.calls[0]


# === LLM-03 — adapters ===================================================


def test_groq_adapter_has_correct_identity() -> None:
    from src.llm.adapters import GroqLlama70B
    adapter = GroqLlama70B(api_key="test_key")
    assert adapter.model_family == "llama"
    assert adapter.model_id == "llama-3.3-70b-versatile"
    assert adapter.max_context == 128_000


def test_groq_adapter_uses_explicit_api_key() -> None:
    """The api_key constructor argument takes precedence over env var."""
    from src.llm.adapters import GroqLlama70B
    # Should not raise even with no GROQ_API_KEY env var.
    with patch.dict(os.environ, {}, clear=True):
        adapter = GroqLlama70B(api_key="explicit_key_123")
        assert adapter.model_family == "llama"


def test_groq_adapter_complete_calls_chat_completions(monkeypatch) -> None:
    from src.llm.adapters import GroqLlama70B
    adapter = GroqLlama70B(api_key="test")

    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="hello world"))]
    adapter._client.chat.completions.create = MagicMock(return_value=fake_response)

    out = adapter._complete("test prompt")
    assert out == "hello world"
    adapter._client.chat.completions.create.assert_called_once()
    call_kwargs = adapter._client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "llama-3.3-70b-versatile"
    assert call_kwargs["temperature"] == 0.0
    assert call_kwargs["messages"] == [{"role": "user", "content": "test prompt"}]


def test_groq_adapter_propagates_rate_limit_error() -> None:
    """RoutingClient catches RateLimitError by type — adapter must not swallow it."""
    import groq
    from src.llm.adapters import GroqLlama70B
    adapter = GroqLlama70B(api_key="test")
    fake_err = groq.RateLimitError(
        message="rate limited",
        response=MagicMock(status_code=429),
        body={},
    )
    adapter._client.chat.completions.create = MagicMock(side_effect=fake_err)
    with pytest.raises(groq.RateLimitError):
        adapter._complete("test")


def test_gemma_adapter_has_correct_identity() -> None:
    from src.llm.adapters import LocalGemma2B
    adapter = LocalGemma2B()
    assert adapter.model_family == "gemma"
    assert adapter.model_id == "google/gemma-2-2b-it"
    assert adapter.max_context == 8_192


def test_gemma_adapter_lazy_loads_model() -> None:
    """Instantiation must not load the ~5 GB weights."""
    from src.llm.adapters import LocalGemma2B
    adapter = LocalGemma2B()
    assert adapter._model is None
    assert adapter._tokenizer is None


def test_gemma_adapter_ensure_loaded_is_idempotent(monkeypatch) -> None:
    from src.llm.adapters import LocalGemma2B
    adapter = LocalGemma2B()

    fake_tokenizer = MagicMock()
    fake_model = MagicMock()
    fake_model.device = "cpu"

    # Patch the lazy imports inside _ensure_loaded.
    import transformers
    monkeypatch.setattr(
        transformers, "AutoTokenizer",
        MagicMock(from_pretrained=MagicMock(return_value=fake_tokenizer)),
    )
    monkeypatch.setattr(
        transformers, "AutoModelForCausalLM",
        MagicMock(from_pretrained=MagicMock(return_value=fake_model)),
    )

    adapter._ensure_loaded()
    first_model = adapter._model
    adapter._ensure_loaded()  # second call should be no-op
    assert adapter._model is first_model


# === LLM-05 — RoutingClient ==============================================


class _ScriptedClient(BaseLLMClient):
    """Stub adapter that raises specific exceptions on demand.

    Used to drive RoutingClient through its rate-limit / network /
    schema-parse paths without touching the real network. Each call to
    `_complete` consumes one entry from `_script`: either a string
    (returned) or an Exception (raised).
    """

    def __init__(self, *, family: str = "llama", model_id: str = "scripted-1"):
        super().__init__(cache=None)
        self._family = family
        self._model_id = model_id
        self._script: list = []
        self.call_count = 0

    @property
    def model_family(self) -> str:
        return self._family

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def max_context(self) -> int:
        return 8192

    def queue(self, *items) -> None:
        self._script.extend(items)

    def _complete(self, prompt: str) -> str:
        self.call_count += 1
        if not self._script:
            return "[]"
        item = self._script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def _make_groq_rate_limit_error():
    import groq
    return groq.RateLimitError(
        message="rate limited",
        response=MagicMock(status_code=429),
        body={},
    )


def _make_groq_network_error():
    import groq
    return groq.APIConnectionError(message="connection failed", request=MagicMock())


def test_routing_proxies_identity_from_primary() -> None:
    from src.llm.routing import RoutingClient
    p = _ScriptedClient(family="llama", model_id="primary-1")
    f = _ScriptedClient(family="gemma", model_id="fallback-1")
    r = RoutingClient(p, f)
    assert r.model_family == "llama"
    assert r.model_id == "primary-1"
    assert r.max_context == 8192


def test_routing_rate_limit_falls_back_immediately() -> None:
    from src.llm.routing import RoutingClient
    p = _ScriptedClient()
    f = _ScriptedClient()
    p.queue(_make_groq_rate_limit_error())
    f.queue("fallback response")
    r = RoutingClient(p, f)
    out = r._complete("test")
    assert out == "fallback response"
    assert p.call_count == 1
    assert f.call_count == 1


def test_routing_network_error_retries_primary_then_falls_back() -> None:
    from src.llm.routing import RoutingClient
    p = _ScriptedClient()
    f = _ScriptedClient()
    p.queue(_make_groq_network_error(), _make_groq_network_error())
    f.queue("fallback response")
    r = RoutingClient(p, f)
    out = r._complete("test")
    assert out == "fallback response"
    assert p.call_count == 2  # original + 1 retry
    assert f.call_count == 1


def test_routing_network_error_succeeds_on_retry() -> None:
    from src.llm.routing import RoutingClient
    p = _ScriptedClient()
    f = _ScriptedClient()
    p.queue(_make_groq_network_error(), "primary recovered")
    r = RoutingClient(p, f)
    out = r._complete("test")
    assert out == "primary recovered"
    assert p.call_count == 2
    assert f.call_count == 0  # fallback never reached


def test_routing_schema_parse_error_falls_back() -> None:
    from src.llm.routing import RoutingClient
    p = _ScriptedClient()
    f = _ScriptedClient()
    p.queue("not valid json at all — no brackets")  # triggers SchemaParseError
    f.queue('["recovered"]')
    r = RoutingClient(p, f)
    out = r.decompose_query("anything", max_sub_questions=4)
    assert out == ["recovered"]


def test_routing_dual_failure_propagates_exception() -> None:
    """If both backends fail with rate-limit, the final exception raises."""
    from src.llm.routing import RoutingClient
    p = _ScriptedClient()
    f = _ScriptedClient()
    p.queue(_make_groq_rate_limit_error())
    f.queue(_make_groq_rate_limit_error())
    r = RoutingClient(p, f)
    import groq
    with pytest.raises(groq.RateLimitError):
        r._complete("test")


def test_routing_unknown_error_propagates() -> None:
    """Non-routable exceptions (not rate-limit, not network) propagate
    untouched. The chain decides what to do."""
    from src.llm.routing import RoutingClient
    p = _ScriptedClient()
    f = _ScriptedClient()
    p.queue(RuntimeError("unexpected"))
    r = RoutingClient(p, f)
    with pytest.raises(RuntimeError, match="unexpected"):
        r._complete("test")
    assert f.call_count == 0  # fallback NOT called for non-routable errors


def test_routing_extract_obligations_falls_back_on_parse_failure() -> None:
    from src.llm.routing import RoutingClient
    p = _ScriptedClient()
    f = _ScriptedClient()
    p.queue("primary garbage no brackets here")
    f.queue('["The deployer shall do something within eight words."]')
    r = RoutingClient(p, f)
    out = r.extract_obligations("sub", regulation_chunks=[])
    assert len(out) == 1
    assert "deployer" in out[0]


@pytest.mark.live_api
def test_groq_adapter_live_call() -> None:
    """Single live Groq call. Skipped by default; run with `pytest -m live_api`."""
    from src.llm.adapters import GroqLlama70B
    if not os.environ.get("GROQ_API_KEY"):
        # Try to load from .env file for local development.
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("GROQ_API_KEY="):
                    os.environ["GROQ_API_KEY"] = line.partition("=")[2].strip()
                    break
    adapter = GroqLlama70B()
    out = adapter._complete("Reply with exactly the word: pong")
    assert "pong" in out.lower()
