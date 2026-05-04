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
