from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys


INCLUDE_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
ENV_RE = re.compile(r"\\begin\s*\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
REF_RE = re.compile(
    r"\\(?:ref|[Cc]ref|[Vv]ref|eqref|autoref|pageref|nameref)\*?"
    r"\s*(?:\[[^\]]*\]\s*)*\{([^}]+)\}"
)
CITE_RE = re.compile(
    r"\\([A-Za-z]*cite[A-Za-z]*)\*?"
    r"\s*(?:\[[^\]]*\]\s*)*\{([^}]+)\}"
)
GRAPHICS_RE = re.compile(r"\\includegraphics\*?(?:\[[^\]]*\])?\s*\{([^}]+)\}")
SECTION_RE = re.compile(
    r"\\(chapter|section|subsection|subsubsection|paragraph|subparagraph)"
    r"(\*)?\s*(?:\[[^\]]*\]\s*)?\{([^}]*)\}"
)
BIB_RE = re.compile(
    r"\\(?:bibliography\s*\{([^}]+)\}|addbibresource(?:\[[^\]]*\])?\s*\{([^}]+)\})"
)
MACRO_START_RE = re.compile(
    r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand)\*?\s*"
    r"(?:\{\\([A-Za-z@]+)\}|\\([A-Za-z@]+))"
)


def strip_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for index, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = index
                break
        lines.append(line[:cut])
    return "\n".join(lines)


def resolve_include(parent: Path, raw_name: str) -> Path:
    candidate = (parent / raw_name.strip()).resolve()
    return candidate if candidate.suffix else candidate.with_suffix(".tex")


def collect_sources(entry: Path) -> tuple[list[Path], str, list[str]]:
    ordered: list[Path] = []
    missing: list[str] = []
    active: list[Path] = []

    def visit(path: Path) -> str:
        resolved = path.resolve()
        if resolved in active:
            chain = " -> ".join(str(item) for item in (*active, resolved))
            raise RuntimeError(f"cyclic LaTeX include: {chain}")
        if not resolved.exists():
            missing.append(str(resolved))
            return ""
        active.append(resolved)
        if resolved not in ordered:
            ordered.append(resolved)
        source = strip_comments(resolved.read_text(encoding="utf-8-sig"))
        parts: list[str] = []
        cursor = 0
        for match in INCLUDE_RE.finditer(source):
            parts.append(source[cursor : match.start()])
            parts.append(visit(resolve_include(resolved.parent, match.group(1))))
            cursor = match.end()
        parts.append(source[cursor:])
        active.pop()
        return "\n".join(parts)

    expanded = visit(entry)
    return ordered, expanded, sorted(set(missing))


def split_keys(groups: list[str]) -> list[str]:
    return [
        key.strip()
        for group in groups
        for key in group.split(",")
        if key.strip() and key.strip() != "*"
    ]


def macro_definitions(text: str) -> tuple[str, dict[str, dict]]:
    definitions: dict[str, dict] = {}
    spans: list[tuple[int, int]] = []
    for match in MACRO_START_RE.finditer(text):
        cursor = match.end()
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        argument_count = 0
        if cursor < len(text) and text[cursor] == "[":
            close = text.find("]", cursor + 1)
            if close == -1:
                continue
            value = text[cursor + 1 : close].strip()
            argument_count = int(value) if value.isdigit() else 0
            cursor = close + 1
            while cursor < len(text) and text[cursor].isspace():
                cursor += 1
            if cursor < len(text) and text[cursor] == "[":
                close = text.find("]", cursor + 1)
                if close == -1:
                    continue
                cursor = close + 1
                while cursor < len(text) and text[cursor].isspace():
                    cursor += 1
        if cursor >= len(text) or text[cursor] != "{":
            continue

        depth = 0
        end = None
        for index in range(cursor, len(text)):
            if text[index] not in "{}":
                continue
            backslashes = 0
            previous = index - 1
            while previous >= 0 and text[previous] == "\\":
                backslashes += 1
                previous -= 1
            if backslashes % 2:
                continue
            depth += 1 if text[index] == "{" else -1
            if depth == 0:
                end = index + 1
                break
        if end is None:
            continue
        name = match.group(1) or match.group(2)
        body = text[cursor + 1 : end - 1]
        definitions[name] = {"argument_count": argument_count, "body": body}
        spans.append((match.start(), end))

    cleaned = list(text)
    for start, end in spans:
        cleaned[start:end] = " " * (end - start)
    return "".join(cleaned), definitions


def manifest(entry: Path) -> dict:
    files, text, missing_includes = collect_sources(entry)
    semantic_text, definitions = macro_definitions(text)
    environments = Counter(ENV_RE.findall(semantic_text))
    labels = LABEL_RE.findall(semantic_text)
    references = split_keys(REF_RE.findall(semantic_text))
    reference_wrappers: dict[str, str] = {}
    for name, definition in definitions.items():
        if definition["argument_count"] != 1:
            continue
        wrapped = split_keys(REF_RE.findall(definition["body"]))
        if wrapped == ["#1"]:
            reference_wrappers[name] = definition["body"]
            calls = re.findall(
                rf"\\{re.escape(name)}\*?\s*(?:\[[^\]]*\]\s*)*\{{([^}}]+)\}}",
                semantic_text,
            )
            references.extend(split_keys(calls))
    citation_matches = CITE_RE.findall(semantic_text)
    citation_groups = [keys for command, keys in citation_matches if command.lower() != "nocite"]
    nocite_groups = [keys for command, keys in citation_matches if command.lower() == "nocite"]
    citation_keys = split_keys(citation_groups)
    graphics = GRAPHICS_RE.findall(semantic_text)
    sections = [
        {"level": level, "starred": bool(star), "title": title.strip()}
        for level, star, title in SECTION_RE.findall(semantic_text)
    ]
    bibliography_files = sorted(
        {
            value.strip()
        for first, second in BIB_RE.findall(semantic_text)
            for value in (first, second)
            if value.strip()
        }
    )

    label_counts = Counter(labels)
    reference_counts = Counter(references)
    citekey_counts = Counter(citation_keys)
    figure_envs = sum(count for name, count in environments.items() if name in {"figure", "figure*"})
    table_envs = sum(count for name, count in environments.items() if name in {"table", "table*"})
    math_names = {"equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*"}
    display_math_envs = sum(count for name, count in environments.items() if name in math_names)

    return {
        "schema_version": 1,
        "kind": "latex-source-manifest",
        "entry_point": str(entry.resolve()),
        "source_files": [str(path) for path in files],
        "missing_includes": missing_includes,
        "sections": sections,
        "environment_counts": dict(sorted(environments.items())),
        "summary": {
            "source_file_count": len(files),
            "section_count": len(sections),
            "figure_environment_count": figure_envs,
            "table_environment_count": table_envs,
            "display_math_environment_count": display_math_envs,
            "includegraphics_count": len(graphics),
            "label_count": len(labels),
            "unique_label_count": len(label_counts),
            "reference_occurrence_count": len(references),
            "unique_referenced_label_count": len(reference_counts),
            "citation_command_count": len(citation_groups),
            "nocite_command_count": len(nocite_groups),
            "cited_key_occurrence_count": len(citation_keys),
            "unique_cited_key_count": len(citekey_counts),
        },
        "labels": dict(sorted(label_counts.items())),
        "references": dict(sorted(reference_counts.items())),
        "citation_keys": dict(sorted(citekey_counts.items())),
        "nocite_keys": sorted(set(split_keys(nocite_groups))),
        "graphics": graphics,
        "bibliography_files": bibliography_files,
        "defined_macros": sorted(definitions),
        "reference_wrapper_macros": sorted(reference_wrappers),
        "duplicate_labels": sorted(name for name, count in label_counts.items() if count > 1),
        "referenced_labels_without_definition": sorted(set(reference_counts) - set(label_counts)),
        "unreferenced_labels": sorted(set(label_counts) - set(reference_counts)),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Generate a read-only semantic manifest for a complete LaTeX entry point.")
    parser.add_argument("entry", type=Path, help="Complete LaTeX entry point")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        report = manifest(args.entry)
        if report["missing_includes"]:
            failures.append("included LaTeX files are missing")
        if report["duplicate_labels"]:
            failures.append("duplicate LaTeX labels")
        if report["referenced_labels_without_definition"]:
            failures.append("LaTeX references have no defined label")
    except (OSError, RuntimeError, UnicodeError) as exc:
        report = {"schema_version": 1, "kind": "latex-source-manifest", "error": str(exc)}
        failures.append("source manifest could not be generated")

    report["ok"] = not failures
    report["failures"] = failures
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
