"""LLM-08 — typing-discipline mock test (FLEX-6 strip-safety).

Mechanically validates that chain code types against the abstract
`LLMClient` interface (LLM-01), never against the concrete
`RoutingClient` (LLM-05) and never against a per-model adapter
(LLM-03).

The test fixture supplies a mock `LLMClient` that implements the ABC
directly — it does *not* subclass `RoutingClient` and does *not*
subclass any adapter — and verifies the chain runs end-to-end
against the mock.

Without this test, the FLEX-6 strip-safety claim is documented but
not enforced. With it, any future code change that types against
`RoutingClient` or a concrete adapter directly will fail this test.

Reference: compliance-gap-analysis-spec.md § LLM-08.
"""

from __future__ import annotations

from src.chain import ComplianceGapChain
from src.llm.adapters import GroqLlama70B, LocalGemma2B
from src.llm.base import BaseLLMClient
from src.llm.client import LLMClient
from src.llm.routing import RoutingClient
from src.schema import validate_register_row


class _DirectLLMClient(LLMClient):
    """LLMClient stub inheriting from the ABC directly.

    DOES NOT inherit from BaseLLMClient (LLM-02), GroqLlama70B (LLM-03),
    LocalGemma2B (LLM-03), or RoutingClient (LLM-05). If chain code ever
    refers to any of those types instead of LLMClient, this test is the
    structural firewall that catches it.
    """

    @property
    def model_family(self) -> str:
        return "direct-stub"

    @property
    def model_id(self) -> str:
        return "direct-stub-1"

    @property
    def max_context(self) -> int:
        return 8192

    def _complete(self, prompt: str) -> str:
        return "[]"

    def decompose_query(self, query, *, max_sub_questions=4):
        return ["a sub-question"]

    def extract_obligations(self, sub_question, regulation_chunks):
        return [
            "The deployer shall conduct a fundamental rights impact assessment."
        ]

    def classify_obligations(self, sub_question, obligations, evidence):
        return [{
            "obligation": obligations[0] if obligations else "",
            "match_status": "partial",
            "evidence_chunk_ids": [],
        }]

    def synthesise_register(self, rows):
        return [
            {**r, "gap_characterisation": "Generic gap text."}
            for r in rows
        ]


class _StubRetriever:
    """Minimal retriever: returns one synthetic chunk per call."""

    def retrieve(self, query, top_k=5, corpus_filter=None):
        from src.ingestion import Chunk
        return [(
            Chunk(
                chunk_id=f"chunk-for-{corpus_filter or 'all'}",
                parent_document_id="doc",
                corpus_tag=(
                    corpus_filter if isinstance(corpus_filter, str) else "REG"
                ),
                document_id="doc",
                section_reference="Section X",
                source_url="",
                chunk_text="some text",
                file_path="x.txt",
                sha256_short="abc",
                sentences=("some text",),
            ),
            0.8,
        )]


def test_chain_runs_with_a_direct_LLMClient_subclass() -> None:
    """The chain accepts a stub that inherits from LLMClient *directly*
    — no concrete adapter, no routing wrapper, no BaseLLMClient
    inheritance. This is FLEX-6 strip-safety in mechanical form."""
    client = _DirectLLMClient()

    # Confirm the stub is structurally distinct from concrete code paths.
    assert isinstance(client, LLMClient)
    assert not isinstance(client, BaseLLMClient)
    assert not isinstance(client, GroqLlama70B)
    assert not isinstance(client, LocalGemma2B)
    assert not isinstance(client, RoutingClient)

    chain = ComplianceGapChain(retriever=_StubRetriever(), client=client)
    rows = chain.run("anything")
    # Chain ran end-to-end. Whatever rows came back must validate.
    for row in rows:
        validate_register_row(row)


def test_routing_client_is_a_LLMClient() -> None:
    """RoutingClient implements the ABC — chain code that types against
    LLMClient accepts it transparently. This test pairs with the one
    above: both 'direct stub' and 'real routing wrapper' satisfy the
    same chain contract."""

    class _NoOpAdapter(BaseLLMClient):
        @property
        def model_family(self) -> str:
            return "noop-llama"

        @property
        def model_id(self) -> str:
            return "noop-1"

        @property
        def max_context(self) -> int:
            return 8192

        def _complete(self, prompt: str) -> str:
            return "[]"

    p = _NoOpAdapter()
    f = _NoOpAdapter()
    r = RoutingClient(p, f)
    assert isinstance(r, LLMClient)
