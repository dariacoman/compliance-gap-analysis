"""LLM-03 — per-model adapters.

Two concrete adapters:

  - GroqLlama70B   primary; Llama 70B served via Groq free tier
  - LocalGemma2B   fallback; Gemma 2-2B-it served on Colab GPU

Each implements `_complete(prompt) -> str` only — ~50–60 lines per
adapter — plus self-contained transport, auth, and (for Gemma) GPU
management. Family-appropriate parsing tolerance (response cleanup,
preamble-stripping, JSON-extraction quirks) lives here, not in the
base class — that's the boundary that makes FLEX-6 strip-safe.

Both adapters must pass the LLM-07 smoke test before being used
in the chain. Adapters propagate rate-limit / network exceptions
in a form `RoutingClient` (LLM-05) can catch.

Reference: compliance-gap-analysis-spec.md § LLM-03.
"""
