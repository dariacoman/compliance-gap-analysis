"""build_chain() factory smoke tests."""

from __future__ import annotations

from src.chain import ComplianceGapChain, build_chain
from src.llm.adapters import GroqLlama70B
from src.llm.routing import RoutingClient


def test_build_chain_default_uses_routing() -> None:
    chain = build_chain()
    assert isinstance(chain, ComplianceGapChain)
    assert isinstance(chain.client, RoutingClient)
    assert chain.client.model_id == "llama-3.3-70b-versatile"


def test_build_chain_no_routing_uses_groq_directly() -> None:
    chain = build_chain(use_routing=False)
    assert isinstance(chain.client, GroqLlama70B)
    assert chain.client.model_id == "llama-3.3-70b-versatile"


def test_build_chain_carries_default_tau_and_top_k() -> None:
    chain = build_chain(use_routing=False)
    assert chain.tau == 0.35
    assert chain.top_k == 5
