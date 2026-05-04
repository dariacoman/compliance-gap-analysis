"""Regenerate computed fields in `corpus/manifest.json` for changed files.

Walks every entry in the manifest, recomputes size_bytes, sha256_short,
and word_count from the actual file content. If any change is detected,
updates the entry's fetch_date to today (UTC). Manual fields
(source_url, doc_pub_date) are preserved untouched.

Run from project root after editing or replacing a corpus file:

  python scripts/regenerate_manifest.py            # update manifest in place
  python scripts/regenerate_manifest.py --dry-run  # report changes only

Exits 0 always; prints a per-entry diff for any changed fields.
"""

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

CORPUS_ROOT = Path("corpus")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without writing")
    args = parser.parse_args()

    manifest_path = CORPUS_ROOT / "manifest.json"
    entries = json.loads(manifest_path.read_text())
    today = datetime.date.today().isoformat()
    changed = 0

    for e in entries:
        full = CORPUS_ROOT / e["path"]
        if not full.exists():
            print(f"SKIP: {e['path']} (file does not exist)")
            continue

        data = full.read_bytes()
        new_size = len(data)
        new_sha = hashlib.sha256(data).hexdigest()[:16]
        new_words = (len(data.decode("utf-8", errors="ignore").split())
                     if e["word_count"] > 0 else 0)

        diffs = []
        if new_size != e["size_bytes"]:
            diffs.append(f"size_bytes {e['size_bytes']} -> {new_size}")
            e["size_bytes"] = new_size
        if new_sha != e["sha256_short"]:
            diffs.append(f"sha256_short {e['sha256_short']} -> {new_sha}")
            e["sha256_short"] = new_sha
        if e["word_count"] > 0 and new_words != e["word_count"]:
            diffs.append(f"word_count {e['word_count']} -> {new_words}")
            e["word_count"] = new_words

        if diffs:
            old_fetch = e.get("fetch_date", "—")
            e["fetch_date"] = today
            diffs.append(f"fetch_date {old_fetch} -> {today}")
            print(f"CHANGED: {e['path']}")
            for d in diffs:
                print(f"  {d}")
            changed += 1

    if changed == 0:
        print("No changes — manifest is up to date.")
        return 0

    print(f"\n{changed} entr{'y' if changed == 1 else 'ies'} updated.")
    if args.dry_run:
        print("(dry-run — manifest.json not written)")
    else:
        manifest_path.write_text(json.dumps(entries, indent=2) + "\n")
        print(f"Wrote {manifest_path}")
        print("Note: corpus/manifest.md is human-edited; update it manually if needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
