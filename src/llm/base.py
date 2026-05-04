"""LLM-02 — BaseLLMClient with concrete task methods.

Concrete task methods that the chain calls without knowing which
model is behind them:

  - decompose_query        — CHN-01 entry point
  - extract_obligations    — CHN-03 entry point
  - classify_obligations   — CHN-04 phase 2 entry point
  - synthesise_register    — CHN-05 entry point

Each task method looks up its prompt from the registry (LLM-04)
keyed on `(task, family)`, calls `_complete()` once (modulo
retry-with-feedback paths in LLM-05), and returns parsed structures.

Concrete-on-base-class shape (rather than abstract on the ABC) is a
deliberate D-008 addendum decision — adapters implement `_complete()`
only and inherit task methods for free. Parsing tolerance lives in
adapters (LLM-03), not in this base class: response cleanup,
preamble-stripping, JSON-extraction quirks vary by model.

Reference: compliance-gap-analysis-spec.md § LLM-02.
"""
