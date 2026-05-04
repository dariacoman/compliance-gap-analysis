"""LLM-04 — prompt registry.

A single Python dict keyed on `(task, family)`. No Jinja, no YAML, no
plugin discovery — the entire prompt set fits inline-readable in this
file. Adding a new model family means adding 4 entries (one per task).

Tasks (must match the four task methods on BaseLLMClient — LLM-02):

  - decompose
  - extract
  - classify
  - synthesise

Families currently supported: `llama`, `gemma`.

Provenance fields (regulation_chunk_ids, confidence) are populated by
chain code post-LLM and never appear in any prompt here.

Prompts at this stage are minimum-viable. They establish the registry
shape and produce parseable JSON output for unit tests; real prompt
tuning happens during CHN-01..05 implementation against actual chain
inputs (per `docs/build-notes.md` § "What NOT to do").

Reference: compliance-gap-analysis-spec.md § LLM-04.
"""

from __future__ import annotations


_DECOMPOSE_LLAMA = """\
You are a regulatory-compliance research assistant. Decompose the \
following compliance query into focused sub-questions, each targeting \
a single regulatory provision or obligation cluster.

Query: {query}

Output ONLY a JSON array of {max_sub_questions} or fewer strings, each \
a self-contained sub-question. Do not include any explanation or \
preamble. Example:
["First sub-question?", "Second sub-question?"]
"""

_DECOMPOSE_GEMMA = """\
Task: split a compliance query into focused sub-questions.

Query: {query}

Output a JSON array of at most {max_sub_questions} strings. Each entry \
must be a self-contained sub-question. Output ONLY the JSON array; no \
preamble, no explanation, no trailing text.

Example output:
["Sub-question one?", "Sub-question two?"]
"""

_EXTRACT_LLAMA = """\
You are a regulatory-compliance research assistant. Read the regulation \
text below and extract the atomic obligations relevant to the \
sub-question. An atomic obligation is a single, verifiable duty placed \
on a specific actor — not a topic, not a theme, not a paragraph summary.

Sub-question: {sub_question}

Regulation text:
{chunks_text}

Output ONLY a JSON array of up to 5 strings, each one an atomic \
obligation. Each obligation should be 8 or more words and contain at \
least one verb. No preamble, no explanation. Example:
["The deployer shall conduct a fundamental rights impact assessment prior to deployment.",
 "The provider shall ensure the system is sufficiently transparent."]
"""

_EXTRACT_GEMMA = """\
Task: extract atomic obligations from regulation text.

Sub-question: {sub_question}

Regulation text:
{chunks_text}

Output a JSON array of at most 5 strings. Each string is one atomic \
obligation: a single duty placed on a specific actor, with a verb, in \
8 or more words. Output ONLY the JSON array.

Example:
["The deployer shall keep automatically generated logs for at least six months.",
 "The provider shall ensure the system meets accuracy requirements."]
"""

_CLASSIFY_LLAMA = """\
You are a compliance auditor. For each obligation below, classify how \
well the deployer-side evidence addresses it. Choose ONE of:
  - silent          (the evidence does not address this obligation)
  - partial         (the evidence touches the obligation but is incomplete)
  - adequate        (the evidence addresses the obligation competently)
  - contradictory   (the evidence contradicts the obligation)

Sub-question: {sub_question}

Obligations:
{obligations}

Deployer-side evidence (policy / extras / guidance):
{evidence}

Output ONLY a JSON array of objects, one per obligation, each with \
keys "obligation" (the obligation text), "match_status" (one of the \
four enum values), and "evidence_chunk_ids" (a list of the chunk_id \
strings that support the verdict; empty list for silent). No preamble.
"""

_CLASSIFY_GEMMA = """\
Classify each obligation against the evidence. Use exactly one of: \
silent, partial, adequate, contradictory.

Sub-question: {sub_question}

Obligations:
{obligations}

Evidence:
{evidence}

Output a JSON array of objects with keys "obligation", "match_status", \
"evidence_chunk_ids". Output ONLY the JSON array. No preamble. No \
explanation outside the JSON.
"""

_SYNTHESISE_LLAMA = """\
You are a compliance auditor producing a residual-risk register. For \
each per-obligation row below, write a `gap_characterisation` field: a \
descriptive sentence stating WHAT ASPECT OF THE OBLIGATION THE POLICY \
FAILS TO ADDRESS. Do not propose remediation; do not say what the \
deployer should do. Describe the gap, not the fix.

Per-obligation rows:
{rows}

Output ONLY a JSON array of objects, each with the same keys as the \
input row plus a `gap_characterisation` string field. No preamble.
"""

_SYNTHESISE_GEMMA = """\
Task: add a `gap_characterisation` field to each row. The field is \
descriptive — what aspect of the obligation the policy fails to \
address. Do NOT propose what the deployer should do.

Rows:
{rows}

Output a JSON array of objects, each with the input keys plus \
`gap_characterisation`. Output ONLY the JSON array. No preamble.
"""


PROMPTS: dict[tuple[str, str], str] = {
    ("decompose",  "llama"): _DECOMPOSE_LLAMA,
    ("decompose",  "gemma"): _DECOMPOSE_GEMMA,
    ("extract",    "llama"): _EXTRACT_LLAMA,
    ("extract",    "gemma"): _EXTRACT_GEMMA,
    ("classify",   "llama"): _CLASSIFY_LLAMA,
    ("classify",   "gemma"): _CLASSIFY_GEMMA,
    ("synthesise", "llama"): _SYNTHESISE_LLAMA,
    ("synthesise", "gemma"): _SYNTHESISE_GEMMA,
}


def render_prompt(task: str, family: str, **kwargs: object) -> str:
    """Look up the prompt for `(task, family)` and substitute kwargs."""
    return PROMPTS[(task, family)].format(**kwargs)
