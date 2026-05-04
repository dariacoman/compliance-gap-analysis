"""LLM-07 — adapter smoke test.

Runs 5 fixed test queries (docs/test-queries.md) through the full
chain against an adapter, asserting:

  (a) JSON parses on the synthesise step's output
  (b) all `match_status` values fall in the enum:
      {silent, partial, adequate, contradictory}
  (c) every non-silent row carries at least one citation
      (policy_evidence | extras_evidence | guidance_evidence)

Runtime under 1 minute on cached LLM calls.

New adapters must pass this smoke test before being used in
evaluation cycles. This catches "swap that mechanically works
but produces garbage" — the FLEX-6 quality bar.

Both shipping adapters (`GroqLlama70B`, `LocalGemma2B`) must pass
this test before the build-completion stage 1 gate.

Reference: compliance-gap-analysis-spec.md § LLM-07.
"""
