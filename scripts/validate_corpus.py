"""Validate the corpus against `corpus/manifest.json`.

Implements the checks specified in v2_corpus_specification.md § 8:

  1. All files in manifest exist on disk
  2. Each text file is non-empty and at least 90% of expected word count
  3. Each manifest entry contains all required fields
  4. SHA-256 hashes match recorded values
  5. (Manual) spot-check: prints 3 random samples per bucket for review

Run from project root:

  python scripts/validate_corpus.py            # checks 1-4
  python scripts/validate_corpus.py --samples  # also prints samples (check 5)

Exits 0 if all checks pass, 1 if any fail.
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

REQUIRED_FIELDS = {"path", "corpus_tag", "size_bytes", "sha256_short",
                   "word_count", "source_url", "doc_pub_date", "fetch_date"}
MIN_WORD_COUNT_RATIO = 0.90  # v2 spec § 8: at least 90% of expected
CORPUS_ROOT = Path("corpus")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", action="store_true",
                        help="print 3 random samples per bucket for manual spot-check")
    args = parser.parse_args()

    manifest_path = CORPUS_ROOT / "manifest.json"
    if not manifest_path.exists():
        print(f"FAIL: manifest not found at {manifest_path}", file=sys.stderr)
        return 1

    entries = json.loads(manifest_path.read_text())
    failures: list[str] = []

    for e in entries:
        # Check 3: required fields present
        missing = REQUIRED_FIELDS - e.keys()
        if missing:
            failures.append(f"{e.get('path', '?')}: missing fields {missing}")
            continue

        full = CORPUS_ROOT / e["path"]

        # Check 1: file exists
        if not full.exists():
            failures.append(f"{e['path']}: file does not exist")
            continue

        data = full.read_bytes()

        # Check 4: SHA-256 matches
        actual_hash = hashlib.sha256(data).hexdigest()[:16]
        if actual_hash != e["sha256_short"]:
            failures.append(f"{e['path']}: hash mismatch "
                            f"(expected {e['sha256_short']}, got {actual_hash})")

        # Check 2: word count >= 90% of expected (skip PDFs recorded as 0 words)
        if e["word_count"] > 0:
            actual_words = len(data.decode("utf-8", errors="ignore").split())
            if actual_words < e["word_count"] * MIN_WORD_COUNT_RATIO:
                failures.append(f"{e['path']}: word count below 90% of expected "
                                f"(expected {e['word_count']}, got {actual_words})")

    print(f"Checked {len(entries)} entries")
    if failures:
        print(f"FAIL: {len(failures)} issue(s):")
        for f in failures:
            print(f"  {f}")
        return 1
    print("PASS: all integrity checks green")

    if args.samples:
        print("\n--- random samples for spot-check ---")
        by_bucket: dict[str, list] = {}
        for e in entries:
            if e["word_count"] == 0:
                continue  # skip binary files (PDFs)
            by_bucket.setdefault(e["corpus_tag"], []).append(e)
        for bucket, bucket_entries in sorted(by_bucket.items()):
            for e in random.sample(bucket_entries, min(3, len(bucket_entries))):
                full = CORPUS_ROOT / e["path"]
                preview = full.read_text(errors="ignore")[:300].replace("\n", " ")
                print(f"\n[{bucket}] {e['path']} ({e['word_count']} words)")
                print(f"  {preview}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
