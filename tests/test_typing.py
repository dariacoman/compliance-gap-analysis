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
`RoutingClient` directly will fail this test.

Test runtime under 30 seconds (no real LLM calls; the mock returns
canned strings).

Reference: compliance-gap-analysis-spec.md § LLM-08.
"""
