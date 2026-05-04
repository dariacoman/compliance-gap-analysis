"""UI-01 — Streamlit primary interface.

Demo path UI. Query input; register output (rows rendered expandably
so column count doesn't crowd the layout); expandable per-corpus
retrieval; sidebar showing retrieval confidence, model in use, and
cache indicator.

Silent rows render with an explanatory marker ("no policy chunk above
similarity τ") — operationalises the abstention cross-cutting concern
in the UI.

Theme: single accent #1E40AF on white background, default Streamlit
fonts, no custom CSS (decisions.md §9). Apply theme once UI-01
functional behaviour is stable; if demo deadline pressure surfaces,
ship with full Streamlit defaults.

If UI-01 destabilises late in the build, fall back to UI-02 (Jupyter)
rather than compress demo polish — Jupyter is brief-acceptable.

Reference: compliance-gap-analysis-spec.md § UI-01.
"""
