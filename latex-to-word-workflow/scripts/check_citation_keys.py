from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from test_better_bibtex import search


def parse_bib(text: str) -> dict[str, dict[str, str]]:
    starts = list(re.finditer(r"(?m)^@(\w+)\{([^,]+),", text))
    entries: dict[str, dict[str, str]] = {}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[match.start():end]
        fields: dict[str, str] = {}
        for name in ("title", "doi"):
            found = re.search(rf"(?ims)^\s*{name}\s*=\s*[{{\"](.+?)[}}\"]\s*,?\s*$", block)
            if found:
                fields[name] = re.sub(r"\s+", " ", found.group(1)).strip()
        entries[match.group(2).strip()] = fields
    return entries


def cited_keys(paths: list[Path]) -> set[str]:
    keys: set[str] = set()
    for path in paths:
        for group in re.findall(r"\\cite\{([^}]+)\}", path.read_text(encoding="utf-8")):
            keys.update(key.strip() for key in group.split(",") if key.strip())
    return keys


def normalize_doi(value: str) -> str:
    return value.lower().removeprefix("https://doi.org/").removeprefix("doi:").strip()


def query_variants(title: str) -> list[str]:
    cleaned = re.sub(r"[{}]", "", title).replace("---", " ").replace("--", " ")
    words = cleaned.split()
    variants = [cleaned]
    variants.extend(" ".join(words[:size]) for size in (10, 7, 5, 3) if len(words) > size)
    return list(dict.fromkeys(value for value in variants if value))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Audit LaTeX citation keys against BibTeX and Better BibTeX.")
    parser.add_argument("--tex", nargs="+", type=Path, required=True, help="LaTeX files or glob-expanded paths")
    parser.add_argument("--bib", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skip-zotero", action="store_true")
    args = parser.parse_args()

    bib = parse_bib(args.bib.read_text(encoding="utf-8"))
    used = sorted(cited_keys(args.tex))
    records = []
    for key in used:
        entry = bib.get(key)
        record: dict = {"key": key, "in_bib": entry is not None}
        if entry is not None and not args.skip_zotero:
            results: list[dict] = []
            for query in query_variants(entry.get("title", "")):
                results = search(query)
                if results:
                    break
            if entry.get("doi"):
                doi = normalize_doi(entry["doi"])
                doi_matches = [item for item in results if normalize_doi(item.get("DOI", "")) == doi]
                if doi_matches:
                    results = doi_matches
            unique = {item.get("citekey") or item.get("citation-key"): item for item in results
                      if item.get("citekey") or item.get("citation-key")}
            record.update({
                "bbt_status": "matched" if len(unique) == 1 else "unmatched" if not unique else "ambiguous",
                "bbt_keys": sorted(unique),
                "item_keys": sorted({item.get("id", "").rsplit("/", 1)[-1] for item in unique.values()}),
            })
        records.append(record)

    report = {
        "cited_key_count": len(used),
        "missing_from_bib": [record["key"] for record in records if not record["in_bib"]],
        "records": records,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)
    failed = report["missing_from_bib"] or any(
        record.get("bbt_status") not in (None, "matched") or
        (record.get("bbt_keys") and record["bbt_keys"] != [record["key"]])
        for record in records
    )
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
