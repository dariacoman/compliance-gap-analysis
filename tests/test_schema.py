"""SCH-01 unit tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.schema import (
    CONFIDENCE_VALUES,
    EvidenceCitation,
    MATCH_STATUS_VALUES,
    RegisterRow,
    validate_register_row,
)


def _adequate_row(**overrides) -> RegisterRow:
    """Build a well-formed adequate-status row for use in tests."""
    defaults = dict(
        regulatory_provision="EU AI Act Article 9",
        regulation_chunk_ids=("regulation/eu-ai-act-2024-1689#article-9",),
        obligation="The provider shall implement a risk management system.",
        match_status="adequate",
        policy_evidence=(
            EvidenceCitation(
                chunk_id="deployer/novara-ai-policy-v3.1#section-3-4",
                section_reference="Novara AI Policy §3.4",
                score=0.78,
            ),
        ),
        extras_evidence=(),
        guidance_evidence=(),
        gap_characterisation="",  # adequate rows can have empty gap text
        confidence="high",
    )
    defaults.update(overrides)
    return RegisterRow(**defaults)


def test_match_status_values_match_spec() -> None:
    assert MATCH_STATUS_VALUES == frozenset({
        "silent", "partial", "adequate", "contradictory",
    })


def test_confidence_values_match_spec() -> None:
    assert CONFIDENCE_VALUES == frozenset({"low", "medium", "high"})


def test_register_row_is_frozen() -> None:
    row = _adequate_row()
    with pytest.raises(FrozenInstanceError):
        row.match_status = "silent"  # type: ignore[misc]


def test_register_row_has_nine_fields() -> None:
    expected_fields = {
        "regulatory_provision", "regulation_chunk_ids", "obligation",
        "match_status", "policy_evidence", "extras_evidence",
        "guidance_evidence", "gap_characterisation", "confidence",
    }
    actual = set(RegisterRow.__dataclass_fields__.keys())
    assert actual == expected_fields


def test_evidence_citation_has_three_fields() -> None:
    expected = {"chunk_id", "section_reference", "score"}
    assert set(EvidenceCitation.__dataclass_fields__.keys()) == expected


def test_validate_accepts_well_formed_row() -> None:
    validate_register_row(_adequate_row())


def test_validate_accepts_silent_row_with_empty_evidence() -> None:
    row = _adequate_row(
        match_status="silent",
        policy_evidence=(),
        extras_evidence=(),
        guidance_evidence=(),
        confidence="high",
        gap_characterisation="The policy does not address Article 27 FRIA.",
    )
    validate_register_row(row)


def test_validate_rejects_unknown_match_status() -> None:
    row = _adequate_row(match_status="unknown")
    with pytest.raises(ValueError, match="match_status"):
        validate_register_row(row)


def test_validate_rejects_unknown_confidence() -> None:
    row = _adequate_row(confidence="very-high")
    with pytest.raises(ValueError, match="confidence"):
        validate_register_row(row)


def test_validate_rejects_silent_row_with_evidence() -> None:
    row = _adequate_row(
        match_status="silent",
        policy_evidence=(
            EvidenceCitation(chunk_id="x", section_reference="X", score=0.6),
        ),
    )
    with pytest.raises(ValueError, match="silent rows must have empty evidence"):
        validate_register_row(row)


def test_validate_rejects_empty_obligation() -> None:
    row = _adequate_row(obligation="")
    with pytest.raises(ValueError, match="obligation"):
        validate_register_row(row)


def test_validate_rejects_empty_regulatory_provision() -> None:
    row = _adequate_row(regulatory_provision="   ")
    with pytest.raises(ValueError, match="regulatory_provision"):
        validate_register_row(row)
