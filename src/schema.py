"""SCH-01 — 9-field per-obligation row schema.

Each row in the residual-risk register represents one atomic obligation:

  - regulatory_provision     citation (e.g., "EU AI Act Article 27")
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

from __future__ import annotations

from dataclasses import dataclass


MATCH_STATUS_VALUES: frozenset[str] = frozenset({
    "silent", "partial", "adequate", "contradictory",
})

CONFIDENCE_VALUES: frozenset[str] = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class EvidenceCitation:
    """One citation in the residual register.

    `chunk_id` provides traceability back to the corpus; `section_reference`
    is the human-readable label rendered in the UI; `score` is the cosine
    similarity at retrieval time, used by `_derive_confidence` post-LLM.
    """
    chunk_id: str
    section_reference: str
    score: float


@dataclass(frozen=True, slots=True)
class RegisterRow:
    """SCH-01 — the 9-field per-obligation row.

    Field set is canonical. `match_status` and `confidence` are enum-bounded
    via module-level constants. Provenance fields (regulation_chunk_ids,
    confidence) are populated post-LLM by chain code; they never appear
    inside any prompt template.
    """
    regulatory_provision: str
    regulation_chunk_ids: tuple[str, ...]
    obligation: str
    match_status: str
    policy_evidence: tuple[EvidenceCitation, ...]
    extras_evidence: tuple[EvidenceCitation, ...]
    guidance_evidence: tuple[EvidenceCitation, ...]
    gap_characterisation: str
    confidence: str


def validate_register_row(row: RegisterRow) -> None:
    """Raise ValueError if any field violates the schema contract."""
    if not isinstance(row, RegisterRow):
        raise ValueError(f"expected RegisterRow, got {type(row).__name__}")
    if row.match_status not in MATCH_STATUS_VALUES:
        raise ValueError(
            f"match_status must be one of {sorted(MATCH_STATUS_VALUES)}, "
            f"got {row.match_status!r}"
        )
    if row.confidence not in CONFIDENCE_VALUES:
        raise ValueError(
            f"confidence must be one of {sorted(CONFIDENCE_VALUES)}, "
            f"got {row.confidence!r}"
        )
    if row.match_status == "silent":
        if row.policy_evidence or row.extras_evidence or row.guidance_evidence:
            raise ValueError(
                "silent rows must have empty evidence in all three corpora"
            )
    # Field-presence (non-None / non-empty) checks for required strings.
    for field_name in ("regulatory_provision", "obligation"):
        value = getattr(row, field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
    # gap_characterisation may be empty for silent rows in some chain
    # implementations (LLM didn't generate one); leave as a soft constraint.
