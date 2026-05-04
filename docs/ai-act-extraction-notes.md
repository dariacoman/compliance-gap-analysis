# AI Act Extraction Notes

> Research observations on `corpus/regulation/eu-ai-act-2024-1689.txt` to inform ING-02 (Article/§-bounded structural chunking with sentence segmentation). Descriptive — not committed code, not a prescription. The chunker should be designed against real text behaviour, not assumptions; this doc captures the real text behaviour so that decision is informed.
>
> The text was extracted from the official EUR-Lex PDF. Total: **11,615 lines, 93,565 words.** This is the largest single file in the corpus and the most complex to chunk.

---

## What's in the file

The Act's structure as it appears in the extracted text:

| Region | Lines (approx.) | Content |
|---|---|---|
| Preamble | 1–60 | Title page, parties, "Having regard to..." block |
| Recitals | ~60–3914 | Numbered explanatory paragraphs (1) through (180) — narrative justifying each provision |
| Articles | 3915–10479 | Articles 1 through 113, the substantive operative provisions |
| Annexes | 10480–11615 | ANNEX I through ANNEX VII (high-risk categories, technical documentation, conformity assessment, etc.) |

For the compliance gap analysis system, the **Articles** and **Annexes** are the load-bearing content — these contain the obligations the system extracts in CHN-03 and matches against deployer documents in CHN-04. **Recitals are interpretive context, not directly enforceable obligations** — including them in the chunk set risks producing chunks that look like obligations but are actually explanatory text. ING-02 should chunk articles and annexes; whether to chunk recitals at all is a design call (see § "Recitals — chunk or skip?" below).

---

## Page furniture (must strip)

The extraction preserved the PDF's page headers and footers. Two repeating noise lines:

- **`PE-CONS 24/24`** — appears 420 times (once per page header). Often accompanied by a routing tag (`AD/DOS/di`) and the section code `TREE.2.B` and language indicator `EN`.
- **`TREE.2.B`** — appears 419 times. Co-located with `PE-CONS` on most pages.

These need to be stripped before chunking, otherwise:
- Chunks straddling a page break will contain noise mid-text
- Embedding quality degrades (the noise pattern is high-frequency and dilutes semantic signal)
- The `top_k_accuracy_score` evaluation in the eval phase becomes unreliable

**Sketch of preprocessing:**

```python
import re

NOISE_PATTERNS = [
    r'^.*PE-CONS \d+/\d+.*$',          # page header line
    r'^\s*TREE\.\d+\.[A-Z]\s*$',        # routing code
    r'^\s*[A-Z]{2,4}\s*$',              # bare two/three-letter codes ('EN', 'AD/DOS')
    r'^\s*\d+\s*$',                     # bare page number
]

def strip_page_furniture(text: str) -> str:
    lines = text.splitlines()
    keep = [ln for ln in lines if not any(re.match(p, ln) for p in NOISE_PATTERNS)]
    return '\n'.join(keep)
```

This is a *sketch* — the patterns above need verification against actual lines (which the chunker should do at write time, not assume). The verification step is part of the **retrieval-config freeze gate's AI Act PDF spot-check** (5–10 chunks manually reviewed).

---

## Article boundary detection

Articles in the file are marked with the article number **centred, alone on its own line**:

```
                                          Article 1
```

(Approximately 30+ leading whitespace characters in the extracted form, depending on the PDF's centring.)

**Sketch regex:**

```python
ARTICLE_BOUNDARY = re.compile(r'^\s{10,}Article\s+(\d+)\s*$')
```

Why `\s{10,}`: the centring uses generous whitespace. Threshold of 10+ leading spaces excludes most inline references (which start at the line's normal indent of ~6 spaces). Adjust based on actual text inspection; a quick `grep -c '^\s\{10,\}Article' corpus/regulation/eu-ai-act-2024-1689.txt` confirms whether the threshold catches the right boundaries.

**What this regex does NOT match (correctly):**

- Inline references like `"Article 114 of the Treaty"` or `"as defined in Article 4(2) TEU"` — these appear within body text at normal indent, not as standalone centred lines
- Article references in cross-references between provisions (`"as referred to in Article 6(2)"`)

**What might still be tricky:**

- Articles containing footnotes that span pages: a footnote marker `(1)` followed by footnote text might appear mid-Article and look like an enumerated provision. ING-02 should preserve enumerated provisions (`1.`, `2.`, `(a)`, `(b)`) as sub-Article structure but not confuse them with footnote markers.
- The first lines after `Article N` are typically the article title (e.g., `"Subject matter"` for Article 1) followed by paragraph 1. The chunker should keep title+paragraph-1 together as the article's lead chunk.

---

## Annex boundary detection

Annexes appear after Article 113. Pattern:

```
ANNEX I        TREE.2.B        EN
```

Same line as the page furniture — annex labels are *also* in the page header during the annex section. So `ANNEX I` repeats many times across the pages of Annex I (5+ occurrences), once per page. This is different from `Article N` which appears only once per article.

**Implication:** can't use `^\s*ANNEX [IVX]+` as a single-occurrence boundary marker — it'll fire many times per annex. Solution: detect *first* appearance of `ANNEX I`, then `ANNEX II`, etc., and use those as boundaries. Or: detect the annex content's structural cues (numbered points within annex) and chunk by those.

**Sketch:**

```python
def find_annex_starts(lines: list[str]) -> dict[str, int]:
    seen = {}
    for i, ln in enumerate(lines):
        m = re.match(r'^\s*ANNEX\s+([IVX]+)\b', ln)
        if m and m.group(1) not in seen:
            seen[m.group(1)] = i
    return seen  # {'I': 10480, 'II': 10614, 'III': 10660, ...}
```

For TalentLens-relevant annex chunks: **Annex III §4** (employment, workers management) is the load-bearing chunk for the test-query Q1. Verify the chunker produces a clean `Annex III §4` chunk during the freeze gate.

---

## Recitals — chunk or skip?

Recitals are numbered explanatory paragraphs (1) through (180), each typically 1–3 sentences explaining the rationale behind a provision. They're not directly binding obligations.

**Three options:**

1. **Skip entirely.** ING-02 starts chunking from line 3915 (Article 1). Cleanest for obligation extraction (CHN-03 won't see recital text and won't extract pseudo-obligations from it). Loses interpretive context that could help with retrieval recall on broad queries.

2. **Chunk separately with a `recital_id` metadata flag.** Allows future chain code to use recitals as supporting context (e.g., a "interpretation note" in the synthesise step) without confusing them with obligations. Adds chunk count.

3. **Chunk inline with articles, no flag.** Simplest. Risk: extraction prompt sees recital text and treats it as an obligation. Most likely to corrupt CHN-03.

**Recommendation:** option 1 (skip). The compliance gap analysis system's distinctive claim is that obligations are extracted from operative provisions and matched against deployer policy. Recitals don't carry obligations; including them adds noise without clear retrieval benefit. If recall on broad queries is poor at the freeze gate, option 2 is the FLEX path.

---

## Sentence segmentation within long articles

Per the spec (ING-02), sentence segmentation uses spaCy's English sentencizer (`spacy.lang.en.English` with `add_pipe("sentencizer")`) — adopted from the week-7 RAG practical for course-material continuity. This applies *within* article boundaries, not across them.

**Things to check at the freeze gate spot-check:**

- Sentences ending with `;` mid-article (legal style) — does sentencizer split or keep together? Legal text uses semicolons heavily for enumerated provisions.
- Numbered/lettered sub-provisions (`1.`, `(a)`, `(i)`) — does sentencizer treat these as sentence boundaries or keep them with the preceding clause? For chunk citation accuracy, keeping the enumeration with its content is preferable.
- Article titles (one or two words like `"Subject matter"`) — sentencizer might treat these as one-word sentences. Acceptable.

If sentencizer produces aggressive splits on legal text, FLEX-3 intermediate (sentence-level retrieval with mean/min/max aggregation) is the recovery path before reaching for a different sentencizer.

---

## What the freeze gate spot-check should verify

Before ING-02 is locked in, manually inspect 5–10 article chunks:

1. **Page furniture stripped?** No `PE-CONS` or `TREE.2.B` text in chunk content.
2. **Article boundary respected?** The chunk for "Article 22" doesn't bleed into "Article 23" content, and vice versa. Easy spot check: read the last 200 chars of an article chunk — does it match the text immediately before the next "Article N" line in the source file?
3. **Sub-Article enumeration preserved?** A chunk for Article 14 should keep `1.`, `2.`, `3.` numbered paragraphs as visible structure, not flatten them into prose.
4. **Footnotes and cross-references inline?** When the article body says `"as defined in Article 3(1)"`, that reference should be preserved within the chunk text (it's content, not a boundary).
5. **Annex III §4 specifically?** This chunk powers test-query Q1 (TalentLens compliance). Verify the chunk contains the employment/workers list (recruitment, advertisement, screening, evaluation of candidates, etc.).

If any of these fail, ING-02 needs adjustment before retrieval recall can be trusted on the 5 hand-written test queries.

---

## What this doc does NOT prescribe

- A specific chunk size in tokens (the spec says 200–800; the chunker should target that range)
- A specific sentence-segmentation strategy beyond using spaCy as the spec dictates
- Whether to include footnotes (they appear in the .txt; treat as inline content unless inspection shows they cause problems)
- Whether to include the title page and "Having regard to..." preamble (probably skip — purely formal)

These are implementation decisions for the ING-02 author. This doc is the input to those decisions, not a substitute for them.
