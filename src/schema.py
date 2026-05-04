"""SCH-01 — 9-field per-obligation row schema.

Each row in the residual-risk register represents one atomic obligation:

  - regulatory_provision     citation (e.g., "GDPR Art 22(3)")
  - regulation_chunk_ids     chunks input to obligation extraction (post-LLM)
  - obligation               atomic obligation text from CHN-03
  - match_status             enum: silent / partial / adequate / contradictory
  - policy_evidence          citations + snippets from Novara policy
  - extras_evidence          citations from DPIA / Model Card / Transparency
                             Notice / Annual Governance Report / Model Intake
  - guidance_evidence        citations from ICO operational guidance
  - gap_characterisation     descriptive (what's unaddressed), not prescriptive
  - confidence               low / medium / high, from retrieval similarity only

Schema is frozen — field changes go through the schema-frozen gate, not
ad-hoc edits. Provenance fields (regulation_chunk_ids, confidence) are
populated post-LLM by chain code and never appear in prompts.

`gap_characterisation` is descriptive (Fork A discipline) — the synthesise
prompt asks "what's unaddressed?", not "what should the deployer do?".

`confidence` derivation: min cosine similarity over cited evidence chunks,
binned at >=0.55 high / >=0.45 medium / else low; silent rows confidence
is "high" (the silence determination is deterministic). See decisions.md
§§1, 2.

Reference: compliance-gap-analysis-spec.md § Group: Output Schema.
"""
