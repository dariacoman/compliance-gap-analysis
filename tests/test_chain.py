"""CHN-01..07 unit + integration tests."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.chain import (
    ComplianceGapChain,
    Obligation,
    _dedupe_chunks_by_id,
    _derive_confidence,
    _derive_regulatory_provision,
    _merge_classifications,
)
from src.ingestion import Chunk
from src.llm.client import LLMClient
from src.schema import EvidenceCitation, RegisterRow, validate_register_row


# === Test helpers — stubs implementing the LLMClient ABC directly ========


def _make_chunk(
    chunk_id: str,
    corpus_tag: str = "REG",
    text: str = "body text content",
    section_reference: str = "Test Reference",
) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        parent_document_id=chunk_id,
        corpus_tag=corpus_tag,
        document_id=chunk_id,
        section_reference=section_reference,
        source_url="",
        chunk_text=text,
        file_path=f"{corpus_tag.lower()}/{chunk_id}.txt",
        sha256_short="abc",
        sentences=(text,),
    )


@dataclass
class _StubLLMClient(LLMClient):
    """LLMClient stub implementing the ABC directly.

    Crucially: does NOT subclass BaseLLMClient, RoutingClient, or any
    concrete adapter. This is also the LLM-08 typing-discipline contract.
    """

    decompose_response: list[str] = None  # type: ignore[assignment]
    extract_response: list[str] = None  # type: ignore[assignment]
    classify_response: list[dict] = None  # type: ignore[assignment]
    synthesise_response: list[dict] = None  # type: ignore[assignment]
    decompose_calls: int = 0
    extract_calls: int = 0
    classify_calls: int = 0
    synthesise_calls: int = 0

    @property
    def model_family(self) -> str:
        return "stub-llama"

    @property
    def model_id(self) -> str:
        return "stub-llama-1"

    @property
    def max_context(self) -> int:
        return 8192

    def _complete(self, prompt: str) -> str:
        return "[]"

    def decompose_query(self, query, *, max_sub_questions=4):
        self.decompose_calls += 1
        return list(self.decompose_response or [])[:max_sub_questions]

    def extract_obligations(self, sub_question, regulation_chunks):
        self.extract_calls += 1
        return list(self.extract_response or [])

    def classify_obligations(self, sub_question, obligations, evidence):
        self.classify_calls += 1
        return list(self.classify_response or [])

    def synthesise_register(self, rows):
        self.synthesise_calls += 1
        return list(self.synthesise_response or [])


class _StubRetriever:
    """Retriever stub that returns pre-programmed responses keyed on filter."""

    def __init__(self) -> None:
        # responses[corpus_filter_key] = list[(chunk, score)]
        self.responses: dict[object, list[tuple[Chunk, float]]] = {}
        self.calls: list[tuple[str, object, int]] = []

    def queue(
        self,
        corpus_filter: str | tuple[str, ...] | None,
        results: list[tuple[Chunk, float]],
    ) -> None:
        self.responses[self._key(corpus_filter)] = results

    @staticmethod
    def _key(corpus_filter):
        if corpus_filter is None:
            return None
        if isinstance(corpus_filter, str):
            return corpus_filter
        return tuple(sorted(corpus_filter))

    def retrieve(self, query, top_k=5, corpus_filter=None):
        self.calls.append((query, corpus_filter, top_k))
        return list(self.responses.get(self._key(corpus_filter), []))


# === Pure-function tests =================================================


def test_derive_confidence_silent_is_high() -> None:
    ob = Obligation(
        text="x",
        sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
        match_status="silent",
    )
    assert _derive_confidence(ob) == "high"


def test_derive_confidence_min_above_055_is_high() -> None:
    ob = Obligation(
        text="x",
        sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
        match_status="adequate",
        policy_evidence=(
            EvidenceCitation("a", "A", 0.7),
            EvidenceCitation("b", "B", 0.6),
        ),
    )
    assert _derive_confidence(ob) == "high"


def test_derive_confidence_min_055_inclusive() -> None:
    ob = Obligation(
        text="x", sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
        match_status="partial",
        policy_evidence=(EvidenceCitation("a", "A", 0.55),),
    )
    assert _derive_confidence(ob) == "high"


def test_derive_confidence_min_above_045_below_055_is_medium() -> None:
    ob = Obligation(
        text="x", sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
        match_status="partial",
        policy_evidence=(
            EvidenceCitation("a", "A", 0.50),
            EvidenceCitation("b", "B", 0.60),  # min is 0.50
        ),
    )
    assert _derive_confidence(ob) == "medium"


def test_derive_confidence_below_045_is_low() -> None:
    ob = Obligation(
        text="x", sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
        match_status="partial",
        policy_evidence=(EvidenceCitation("a", "A", 0.40),),
    )
    assert _derive_confidence(ob) == "low"


def test_derive_confidence_no_evidence_is_low() -> None:
    ob = Obligation(
        text="x", sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
        match_status="partial",
    )
    assert _derive_confidence(ob) == "low"


def test_derive_regulatory_provision_uses_top_chunk() -> None:
    chunks = [
        (_make_chunk("c1", section_reference="EU AI Act Article 27"), 0.9),
        (_make_chunk("c2", section_reference="EU AI Act Article 28"), 0.7),
    ]
    assert _derive_regulatory_provision(chunks) == "EU AI Act Article 27"


def test_derive_regulatory_provision_empty_returns_placeholder() -> None:
    assert _derive_regulatory_provision([]) == "(no regulation chunks)"


def test_dedupe_chunks_by_id_preserves_order() -> None:
    a, b, c = _make_chunk("a"), _make_chunk("b"), _make_chunk("c")
    out = _dedupe_chunks_by_id([a, b, a, c, b])
    assert [x.chunk_id for x in out] == ["a", "b", "c"]


def test_merge_classifications_filters_hallucinated_chunk_ids() -> None:
    ob = Obligation(
        text="x", sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
        policy_evidence=(
            EvidenceCitation("real-1", "R1", 0.8),
            EvidenceCitation("real-2", "R2", 0.7),
        ),
    )
    classifications = [{
        "obligation": "x",
        "match_status": "partial",
        "evidence_chunk_ids": ["real-1", "hallucinated-id"],
    }]
    merged = _merge_classifications([ob], classifications)
    assert len(merged) == 1
    assert merged[0].match_status == "partial"
    # Only "real-1" survives the filter; "hallucinated-id" is dropped.
    assert [c.chunk_id for c in merged[0].policy_evidence] == ["real-1"]


def test_merge_classifications_unknown_status_falls_back_to_partial() -> None:
    ob = Obligation(
        text="x", sub_question="y",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
    )
    classifications = [{"match_status": "weird-not-an-enum-value"}]
    merged = _merge_classifications([ob], classifications)
    assert merged[0].match_status == "partial"


# === Step-method unit tests with stubs ===================================


def _build_chain_with_stubs(
    *,
    decompose=None, extract=None, classify=None, synthesise=None,
    retriever=None, verbose=False,
):
    client = _StubLLMClient(
        decompose_response=decompose or [],
        extract_response=extract or [],
        classify_response=classify or [],
        synthesise_response=synthesise or [],
    )
    retriever = retriever or _StubRetriever()
    return ComplianceGapChain(retriever, client, verbose=verbose), client, retriever


def test_decompose_calls_client_with_max_sub_questions() -> None:
    chain, client, _r = _build_chain_with_stubs(
        decompose=["q1", "q2", "q3", "q4", "q5"]
    )
    out = chain._decompose("any query")
    assert client.decompose_calls == 1
    # max_sub_questions=4 cap honoured by stub
    assert len(out) == 4


def test_retrieve_regulation_uses_REG_filter() -> None:
    r = _StubRetriever()
    r.queue("REG", [(_make_chunk("c1"), 0.9)])
    chain, _c, _r = _build_chain_with_stubs(retriever=r)
    out = chain._retrieve_regulation("any sub-question")
    assert len(out) == 1
    assert r.calls[0][1] == "REG"


def test_extract_obligations_constructs_obligations_with_chunk_ids() -> None:
    chain, _c, _r = _build_chain_with_stubs(
        extract=["The deployer shall do something with eight or more words."]
    )
    reg = [
        (_make_chunk("regulation/x", section_reference="EU AI Act Article 9"), 0.85),
        (_make_chunk("regulation/y", section_reference="EU AI Act Article 10"), 0.70),
    ]
    out = chain._extract_obligations("sub-q", reg)
    assert len(out) == 1
    assert out[0].regulation_chunk_ids == ("regulation/x", "regulation/y")
    # provision = top chunk's section_reference
    assert out[0].regulatory_provision == "EU AI Act Article 9"


def test_match_phase1_marks_silent_when_max_sim_below_tau() -> None:
    """For an obligation whose deployer-side retrieval returns max < τ,
    chain marks silent without invoking Phase 2."""
    r = _StubRetriever()
    # All three corpora return chunks below τ=0.35
    r.queue("DEP", [(_make_chunk("d1", "DEP"), 0.20)])
    r.queue("DEP_EXTRAS", [(_make_chunk("e1", "DEP_EXTRAS"), 0.18)])
    r.queue("OPS", [(_make_chunk("o1", "OPS"), 0.25)])
    chain, client, _ = _build_chain_with_stubs(retriever=r)
    ob = Obligation(
        text="silent obligation text",
        sub_question="sq",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
    )
    result = chain._match("sq", [ob])
    assert len(result) == 1
    assert result[0].match_status == "silent"
    # Phase 2 NOT called
    assert client.classify_calls == 0
    # Silent rows have empty evidence
    assert result[0].policy_evidence == ()


def test_match_phase2_runs_when_obligation_above_tau() -> None:
    r = _StubRetriever()
    r.queue("DEP", [(_make_chunk("d1", "DEP"), 0.65)])
    r.queue("DEP_EXTRAS", [])
    r.queue("OPS", [(_make_chunk("o1", "OPS"), 0.50)])
    chain, client, _ = _build_chain_with_stubs(
        retriever=r,
        classify=[{
            "obligation": "ob text",
            "match_status": "partial",
            "evidence_chunk_ids": ["d1", "o1"],
        }],
    )
    ob = Obligation(
        text="ob text",
        sub_question="sq",
        regulation_chunk_ids=("c1",),
        regulatory_provision="P",
    )
    result = chain._match("sq", [ob])
    assert client.classify_calls == 1
    assert len(result) == 1
    assert result[0].match_status == "partial"
    # Both d1 and o1 should be retained (real chunk_ids kept)
    cited = [c.chunk_id for c in result[0].policy_evidence + result[0].guidance_evidence]
    assert "d1" in cited
    assert "o1" in cited


def test_match_skips_phase2_when_all_silent() -> None:
    r = _StubRetriever()
    r.queue("DEP", [])
    r.queue("DEP_EXTRAS", [])
    r.queue("OPS", [])
    chain, client, _ = _build_chain_with_stubs(retriever=r)
    obs = [
        Obligation(text="o1", sub_question="sq", regulation_chunk_ids=("c",), regulatory_provision="P"),
        Obligation(text="o2", sub_question="sq", regulation_chunk_ids=("c",), regulatory_provision="P"),
    ]
    result = chain._match("sq", obs)
    assert all(ob.match_status == "silent" for ob in result)
    assert client.classify_calls == 0


def test_synthesise_produces_validated_register_rows() -> None:
    chain, client, _ = _build_chain_with_stubs(
        synthesise=[{
            "obligation": "ob text",
            "gap_characterisation": "Policy doesn't address X.",
        }],
    )
    ob = Obligation(
        text="ob text",
        sub_question="sq",
        regulation_chunk_ids=("c1",),
        regulatory_provision="EU AI Act Article 9",
        match_status="silent",
    )
    rows = chain._synthesise([ob])
    assert client.synthesise_calls == 1
    assert len(rows) == 1
    validate_register_row(rows[0])
    assert rows[0].confidence == "high"  # silent
    assert rows[0].gap_characterisation == "Policy doesn't address X."


def test_synthesise_empty_input_returns_empty() -> None:
    chain, client, _ = _build_chain_with_stubs()
    assert chain._synthesise([]) == []
    assert client.synthesise_calls == 0


def test_run_end_to_end_with_stubs() -> None:
    r = _StubRetriever()
    r.queue("REG", [
        (_make_chunk("regulation/r1", "REG", section_reference="EU AI Act Article 27"), 0.85)
    ])
    # All deployer-side returns below τ → silent
    r.queue("DEP", [])
    r.queue("DEP_EXTRAS", [])
    r.queue("OPS", [])
    chain, client, _ = _build_chain_with_stubs(
        decompose=["sub-q-1"],
        extract=["The deployer shall conduct an FRIA prior to deployment."],
        synthesise=[{
            "obligation": "The deployer shall conduct an FRIA prior to deployment.",
            "gap_characterisation": "FRIA process is not described.",
        }],
        retriever=r,
    )
    rows = chain.run("user query")
    assert len(rows) == 1
    assert rows[0].match_status == "silent"
    assert rows[0].confidence == "high"
    assert rows[0].regulatory_provision == "EU AI Act Article 27"
    assert client.decompose_calls == 1
    assert client.extract_calls == 1
    assert client.classify_calls == 0  # no Phase 2 needed
    assert client.synthesise_calls == 1


def test_run_with_empty_decomposition_returns_empty() -> None:
    chain, _c, _r = _build_chain_with_stubs(decompose=[])
    assert chain.run("anything") == []


def test_verbose_mode_prints_stage_labels(capsys) -> None:
    chain, _c, _r = _build_chain_with_stubs(decompose=["x"], verbose=True)
    chain._decompose("test query")
    captured = capsys.readouterr()
    assert "[CHN-01]" in captured.out


def test_chain_types_against_LLMClient_abc() -> None:
    """LLM-08 typing-discipline contract: chain accepts a stub LLMClient
    that does NOT inherit BaseLLMClient or any concrete adapter."""
    chain, client, _r = _build_chain_with_stubs()
    assert isinstance(client, LLMClient)
    # Importantly: NOT a BaseLLMClient
    from src.llm.base import BaseLLMClient
    assert not isinstance(client, BaseLLMClient)
    # Chain holds the stub directly
    assert chain.client is client


# === Real-corpus integration ============================================


def test_q5_fria_integration_runs_end_to_end(corpus_retriever) -> None:
    """Q5 FRIA: full pipeline against real corpus + retriever with a
    stub LLM. Whether the FRIA obligation classifies silent vs partial
    depends on the actual cosine distribution against deployer-side
    chunks — that's a τ-calibration question for the freeze gate, not a
    chain unit-test bar. The structural assertion: chain runs end-to-end
    and every output row passes schema validation.
    """
    fria_obligation = (
        "The deployer shall conduct a fundamental rights impact "
        "assessment prior to deploying a high-risk AI system."
    )
    client = _StubLLMClient(
        decompose_response=[
            "Have we performed an FRIA under EU AI Act Article 27 for TalentLens?"
        ],
        extract_response=[fria_obligation],
        # If Phase 1 doesn't silence, Phase 2 runs and we provide a
        # canned partial classification so the chain produces a row.
        classify_response=[{
            "obligation": fria_obligation,
            "match_status": "partial",
            "evidence_chunk_ids": [],
        }],
        synthesise_response=[{
            "obligation": fria_obligation,
            "gap_characterisation": "Policy does not specifically address Article 27 FRIA.",
        }],
    )
    chain = ComplianceGapChain(corpus_retriever, client)
    rows = chain.run("Have we performed a FRIA under EU AI Act Article 27?")
    assert len(rows) >= 1
    for row in rows:
        validate_register_row(row)


def test_chain_run_validates_all_output_rows(corpus_retriever) -> None:
    """Every RegisterRow returned by run() passes validate_register_row."""
    client = _StubLLMClient(
        decompose_response=["What does the AI Act say about high-risk AI systems?"],
        extract_response=[
            "The provider shall implement a risk management system for high-risk AI."
        ],
        classify_response=[{
            "obligation": "The provider shall implement a risk management system for high-risk AI.",
            "match_status": "partial",
            "evidence_chunk_ids": [],
        }],
        synthesise_response=[{
            "obligation": "The provider shall implement a risk management system for high-risk AI.",
            "gap_characterisation": "Risk management partly addressed.",
        }],
    )
    chain = ComplianceGapChain(corpus_retriever, client)
    rows = chain.run("What about high-risk AI?")
    for row in rows:
        validate_register_row(row)  # raises if invalid
        assert isinstance(row, RegisterRow)
