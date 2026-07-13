# LaTeX to Word Workflow

An Agent Skill for converting LaTeX manuscripts into polished, editable Microsoft Word documents. It supports figures, equations, tables, custom Word styles, static CSL references, and native Zotero citation fields that remain refreshable in Word.

## Highlights

- Convert LaTeX directly to DOCX with Pandoc.
- Use a reusable `reference.docx` to control Word formatting.
- Preserve live Zotero citations through Better BibTeX's official `zotero.lua` filter.
- Audit citation keys across LaTeX, BibTeX, and Zotero.
- Assign dedicated Word styles to figures, captions, tables, and bibliographies.
- Validate DOCX relationships and verify that Microsoft Word opens the result without repair.
- Guide first-time users through template preparation and a one-citation smoke test.

## Repository layout

The installable skill is in [`latex-to-word-workflow/`](latex-to-word-workflow/). The repository-level files are only for distribution and licensing.

## Installation

Copy or clone the `latex-to-word-workflow` directory into the skills directory used by your Agent Skills-compatible tool.

For Codex on Windows, a typical destination is:

```text
%USERPROFILE%\.codex\skills\latex-to-word-workflow
```

Example with Git:

```powershell
git clone https://github.com/hajimi-kun/latex-to-word-workflow.git
Copy-Item -Recurse .\latex-to-word-workflow\latex-to-word-workflow "$env:USERPROFILE\.codex\skills\"
```

Other Agent Skills-compatible tools can use the same skill folder and its standard `SKILL.md` entry. The optional `agents/openai.yaml` supplies OpenAI-specific interface metadata and may be ignored elsewhere.

## First use

Ask your agent to use the skill for a LaTeX-to-Word conversion. On an unconfigured computer, the skill instructs the agent to:

1. detect Pandoc, Python, LaTeX, Word, Zotero, and Better BibTeX;
2. prepare and confirm a project-specific Word template;
3. verify one real Better BibTeX citation key;
4. generate a one-citation test document;
5. confirm that Word and Zotero can refresh the citation and create the bibliography; and
6. convert the full manuscript only after the test passes.

See [`SKILL.zh-CN.md`](latex-to-word-workflow/SKILL.zh-CN.md) for the Chinese-readable skill guide.

## Main requirements

- Pandoc 3+
- Python with `python-docx`
- LaTeX/BibTeX toolchain
- Microsoft Word on Windows
- Zotero, the Zotero Word plugin, Better BibTeX, and the official `zotero.lua` filter for live citations

Static CSL conversion can be used without Zotero and Better BibTeX.

## License

MIT License. See [LICENSE](LICENSE).
