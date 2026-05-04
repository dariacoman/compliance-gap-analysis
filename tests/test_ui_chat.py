"""UI-02 chat loop + print_register tests."""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Iterator

import pytest

from src.schema import EvidenceCitation, RegisterRow
from src.ui.notebook_chat import chat, print_register


def _silent_row() -> RegisterRow:
    return RegisterRow(
        regulatory_provision="EU AI Act Article 27",
        regulation_chunk_ids=("regulation/eu-ai-act-2024-1689#article-27",),
        obligation="The deployer shall conduct a fundamental rights impact assessment.",
        match_status="silent",
        policy_evidence=(),
        extras_evidence=(),
        guidance_evidence=(),
        gap_characterisation="Policy does not address Article 27 FRIA.",
        confidence="high",
    )


def _adequate_row() -> RegisterRow:
    return RegisterRow(
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
        gap_characterisation="",
        confidence="high",
    )


def test_print_register_empty_input() -> None:
    buf = io.StringIO()
    print_register([], file=buf)
    assert "no rows produced" in buf.getvalue()


def test_print_register_summary_counts() -> None:
    buf = io.StringIO()
    print_register([_silent_row(), _silent_row(), _adequate_row()], file=buf)
    out = buf.getvalue()
    assert "2 silent" in out
    assert "1 adequate" in out
    assert "🔴" in out
    assert "🟢" in out


def test_print_register_silent_marker_present() -> None:
    buf = io.StringIO()
    print_register([_silent_row()], file=buf)
    out = buf.getvalue()
    assert "Silent" in out
    assert "no policy chunk above similarity" in out


def test_print_register_obligation_text() -> None:
    buf = io.StringIO()
    print_register([_silent_row()], file=buf)
    assert "fundamental rights impact assessment" in buf.getvalue()


def test_print_register_evidence_listed() -> None:
    buf = io.StringIO()
    print_register([_adequate_row()], file=buf)
    out = buf.getvalue()
    assert "Novara AI Policy §3.4" in out
    assert "0.780" in out  # score formatting
    assert "[deployer/novara-ai-policy-v3.1#section-3-4]" in out


def test_print_register_includes_confidence_and_provision() -> None:
    buf = io.StringIO()
    print_register([_adequate_row()], file=buf)
    out = buf.getvalue()
    assert "ADEQUATE" in out
    assert "EU AI Act Article 9" in out
    assert "high" in out


def test_print_register_lists_regulation_provenance() -> None:
    buf = io.StringIO()
    print_register([_silent_row()], file=buf)
    assert "Regulation provenance" in buf.getvalue()
    assert "regulation/eu-ai-act-2024-1689#article-27" in buf.getvalue()


# === chat() loop tests using a stub chain + monkey-patched input =======


@dataclass
class _StubChain:
    """Minimal chain stand-in for chat() loop tests."""
    rows_to_return: list[RegisterRow] = None  # type: ignore[assignment]
    raise_on_run: bool = False
    run_calls: int = 0
    tau: float = 0.35
    top_k: int = 5

    @property
    def client(self):
        @dataclass
        class _C:
            model_id: str = "stub-model"
        return _C()

    def run(self, query: str):
        self.run_calls += 1
        if self.raise_on_run:
            raise RuntimeError("simulated chain failure")
        return list(self.rows_to_return or [])


def _scripted_input(commands: list[str]) -> Iterator[str]:
    for cmd in commands:
        yield cmd
    raise EOFError()


@pytest.fixture
def scripted_input(monkeypatch):
    def _setup(commands: list[str]):
        gen = _scripted_input(commands)
        monkeypatch.setattr("builtins.input", lambda *_a, **_kw: next(gen))
    return _setup


def test_chat_exits_on_exit_command(scripted_input, capsys) -> None:
    scripted_input(["exit"])
    chain = _StubChain()
    chat(chain)
    assert chain.run_calls == 0
    out = capsys.readouterr().out
    assert "Compliance Gap Analysis — chat mode" in out


def test_chat_exits_on_quit_command(scripted_input) -> None:
    scripted_input(["quit"])
    chain = _StubChain()
    chat(chain)
    assert chain.run_calls == 0


def test_chat_exits_on_eof(scripted_input) -> None:
    scripted_input([])  # immediate EOFError
    chain = _StubChain()
    chat(chain)  # must not raise
    assert chain.run_calls == 0


def test_chat_skips_empty_input(scripted_input) -> None:
    scripted_input(["", "  ", "exit"])
    chain = _StubChain()
    chat(chain)
    assert chain.run_calls == 0


def test_chat_runs_chain_on_query_and_prints_register(
    scripted_input, capsys
) -> None:
    scripted_input(["my compliance query?", "exit"])
    chain = _StubChain(rows_to_return=[_silent_row()])
    chat(chain)
    assert chain.run_calls == 1
    out = capsys.readouterr().out
    assert "Silent" in out
    assert "fundamental rights impact assessment" in out


def test_chat_swallows_chain_exception(scripted_input, capsys) -> None:
    scripted_input(["bad query", "exit"])
    chain = _StubChain(raise_on_run=True)
    chat(chain)  # must not raise
    out = capsys.readouterr().out
    assert "ERROR" in out
    assert "RuntimeError" in out


def test_chat_uses_injected_chain_not_default(scripted_input) -> None:
    """chat(chain=injected) must NOT call build_chain()."""
    scripted_input(["exit"])
    chain = _StubChain()
    chat(chain)
    # If build_chain() had been called, it would have constructed a real
    # chain (slow). Stub-only execution is sub-second.
