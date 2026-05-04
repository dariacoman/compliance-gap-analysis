"""LLM-04 — prompt registry.

A single Python dict keyed on `(task, family)`. No Jinja, no YAML, no
plugin discovery — the entire prompt set fits inline-readable in this
file. Adding a new model family means adding 4 entries (one per task).

Tasks (must match the four task methods on BaseLLMClient — LLM-02):

  - decompose_query
  - extract_obligations
  - classify_obligations
  - synthesise_register

Families currently supported: `llama`, `gemma`.

Provenance fields (regulation_chunk_ids, confidence) are populated by
chain code post-LLM and never appear in any prompt here.

Prompts get drafted alongside the chain step that consumes them, not
in advance — pre-writing locks in imagined output shapes. See
build-notes.md "What NOT to do".

Reference: compliance-gap-analysis-spec.md § LLM-04.
"""
