"""ING-01, ING-02, ING-03 — corpus ingestion.

Loads the four-bucket corpus (regulation, ICO operational guidance,
Novara deployer policy, Novara deployer-extras) into typed chunk
records (ING-01); chunks legal texts at Article/§ boundaries with
sentence segmentation within larger units (ING-02); embeds chunks
with `multi-qa-MiniLM-L6-cos-v1` and caches them on disk (ING-03).

Pre-conditions: `corpus/manifest.json` complete, hashes verified
(`scripts/validate_corpus.py` passes).

Outputs: typed chunk records carrying corpus_tag, document_id,
section_reference, source_url, chunk_id, chunk_text, plus an
on-disk embedding cache under `embeddings/`.

Reference: compliance-gap-analysis-spec.md § Group: Ingestion.
AI Act extraction observations: docs/ai-act-extraction-notes.md.
"""
