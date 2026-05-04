"""LLM-05 — RoutingClient with hardcoded policy.

Wraps primary (Llama 70B via Groq) + fallback (Gemma 2-2B on Colab)
with hardcoded routing policy:

  - rate-limit error      -> immediate fallback to Gemma
  - network error         -> 1 retry on primary, then fallback
  - schema-parse failure  -> 1 retry-with-feedback on primary, then fallback

If both backends fail (dual-backend failure), surface a visible error
message rather than emit a malformed register — no silent partial
outputs.

Implements the `LLMClient` ABC (LLM-01) so the chain doesn't know it's
there. Hardcoded policy was a deliberate decision over configurable —
three exception types are known, three actions are known; making it
configurable would be unused machinery at this scale.

This is one wrapper class, not an architectural layer. ~50 lines.

FLEX-6 strip-down: once dual-backend reliability is demonstrated and
the eval surface no longer needs Gemma, this file + the unused adapter
+ family-keyed prompts are cleanly removable (~150 lines total). The
ABC, base class task methods, prompt registry, smoke test, and cache
keying all stay (prompt-hygiene infrastructure).

Reference: compliance-gap-analysis-spec.md § LLM-05.
"""
