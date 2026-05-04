"""UI-02 — chat loop for the compliance gap chain.

Wraps ComplianceGapChain in a NewsReader-style chat() loop:
  query in -> register out -> loop until exit.

Plain-text rendering with ASCII separators + emoji status glyphs
that work in any terminal, any Jupyter kernel output, and in plain
stdout. No IPython.display dependency.

Reference: compliance-gap-analysis-spec.md § UI-02.
"""

from __future__ import annotations

import sys
from typing import Optional

from src.chain import ComplianceGapChain, build_chain
from src.schema import RegisterRow


_STATUS_GLYPH: dict[str, str] = {
    "silent": "🔴",
    "partial": "🟠",
    "adequate": "🟢",
    "contradictory": "🟣",
}


def chat(chain: Optional[ComplianceGapChain] = None) -> None:
    """Interactive query loop. Type 'exit' or Ctrl-D to quit.

    Constructs a default chain via `build_chain()` if none is provided.
    Tests inject a stub to avoid touching the real LLM.
    """
    if chain is None:
        chain = build_chain()
    print("=" * 70)
    print("Compliance Gap Analysis — chat mode")
    print(
        f"Model: {chain.client.model_id} · τ={chain.tau} · top_k={chain.top_k}"
    )
    print("Type a compliance query, or 'exit' to quit.")
    print("=" * 70)
    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in ("exit", "quit"):
            break
        if not query:
            continue
        try:
            rows = chain.run(query)
        except Exception as exc:
            print(f"  ERROR: {type(exc).__name__}: {exc}")
            continue
        print_register(rows)


def print_register(
    rows: list[RegisterRow], file=None
) -> None:
    """Render a list of RegisterRows as plain text.

    `file=None` resolves to `sys.stdout` at call time (not import time)
    so pytest's capsys / monkeypatched stdout works as expected.
    """
    if file is None:
        file = sys.stdout
    if not rows:
        print("(no rows produced)", file=file)
        return
    counts = {"silent": 0, "partial": 0, "adequate": 0, "contradictory": 0}
    for r in rows:
        counts[r.match_status] = counts.get(r.match_status, 0) + 1
    print(file=file)
    print("─" * 70, file=file)
    print(
        f"Register: {len(rows)} rows · "
        f"🔴 {counts['silent']} silent · "
        f"🟠 {counts['partial']} partial · "
        f"🟢 {counts['adequate']} adequate · "
        f"🟣 {counts['contradictory']} contradictory",
        file=file,
    )
    print("─" * 70, file=file)
    for i, row in enumerate(rows, 1):
        glyph = _STATUS_GLYPH.get(row.match_status, "?")
        header = (
            f"\n[{i}] {glyph} {row.match_status.upper():14s} "
            f"conf={row.confidence:6s} {row.regulatory_provision}"
        )
        print(header, file=file)
        print(f"    Obligation: {row.obligation}", file=file)
        if row.match_status == "silent":
            print(
                "    ⚠ Silent: no policy chunk above similarity τ "
                "— policy is silent on this obligation.",
                file=file,
            )
        if row.gap_characterisation:
            print(f"    Gap:        {row.gap_characterisation}", file=file)
        n_pol = len(row.policy_evidence)
        n_ext = len(row.extras_evidence)
        n_gui = len(row.guidance_evidence)
        if n_pol + n_ext + n_gui:
            print(
                f"    Evidence:   {n_pol} policy · {n_ext} extras · {n_gui} guidance",
                file=file,
            )
            for cit in (
                list(row.policy_evidence)
                + list(row.extras_evidence)
                + list(row.guidance_evidence)
            ):
                print(
                    f"      - [{cit.chunk_id}] {cit.section_reference} "
                    f"(score: {cit.score:.3f})",
                    file=file,
                )
        if row.regulation_chunk_ids:
            print(
                f"    Regulation provenance: "
                f"{', '.join(row.regulation_chunk_ids)}",
                file=file,
            )
