"""LLM-06 — disk response cache.

Cache keyed on `(rendered_prompt, model_id)` so different models never
pollute each other's cached outputs and eval-phase replay is
deterministic.

Serves four purposes:

  - Rate-limit safety (cache hits don't burn API quota)
  - Dev iteration speed (cache hits are sub-second)
  - Demo pre-warming (planned demo queries are pre-warmed; demo
    latency is sub-second under any backend)
  - Evaluation reproducibility (eval-phase replay against the same
    model produces identical cached outputs)

Cache lives at `llm_cache/` (gitignored). Re-running the chain against
the same query + same model hits the cache and bypasses both the
network and the LLM completely.

Note: Opus (gold-set bootstrap script in eval phase) is NOT routed
through this cache — it's a one-off script outside the FLEX-6
abstraction.

Reference: compliance-gap-analysis-spec.md § LLM-06.
"""
