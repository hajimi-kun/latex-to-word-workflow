# LaTeX to Word Workflow

Agent Skill: convert LaTeX manuscripts into polished, editable Microsoft Word (DOCX) with figures, equations, tables, custom styles, static CSL references, and optional live Zotero citation fields.

Current version: **2.0.0**

## Highlights

- Pandoc LaTeX → DOCX with a reusable `reference.docx`
- Live Zotero via Better BibTeX’s official `zotero.lua`, or static CSL without Zotero
- Citation-key audit (BibTeX ± Better BibTeX)
- Native Word `SEQ`/`REF` for figures, tables, and labeled equations, with cross-ref audit
- Style mapping for figures, captions, tables, bibliographies
- DOCX relationship / cross-ref package checks; final Word refresh and visual check by the user

## Layout

Installable skill: [`latex-to-word-workflow/`](latex-to-word-workflow/). Repo root holds distribution files only.

## Install

Copy or clone the inner `latex-to-word-workflow` folder into your Agent Skills directory.

Examples:

| Tool | Typical path |
|---|---|
| Codex (Windows) | `%USERPROFILE%\.codex\skills\latex-to-word-workflow` |
| Claude Code | `~/.claude/skills/latex-to-word-workflow` |
| Other | Any skills root that loads a folder with `SKILL.md` |

```powershell
git clone https://github.com/hajimi-kun/latex-to-word-workflow.git
Copy-Item -Recurse .\latex-to-word-workflow\latex-to-word-workflow "$env:USERPROFILE\.codex\skills\"
```

```bash
git clone https://github.com/hajimi-kun/latex-to-word-workflow.git
cp -R latex-to-word-workflow/latex-to-word-workflow ~/.claude/skills/
```

Optional `agents/openai.yaml` is OpenAI/Codex UI metadata; other hosts may ignore it.

Python deps (from the skill directory):

```text
pip install -r requirements.txt
```

## First use

Ask the agent to convert with this skill. On an unconfigured machine it should:

1. Detect Pandoc, Python, LaTeX, Word, and (if needed) Zotero/BBT
2. Copy/confirm a project Word template
3. Smoke-test with `examples/minimal/` (one real BBT key for live mode)
4. Only then convert the full manuscript

Details: [`references/first-run-setup.md`](latex-to-word-workflow/references/first-run-setup.md).
Chinese guide: [`SKILL.zh-CN.md`](latex-to-word-workflow/SKILL.zh-CN.md).

## Requirements

- Pandoc 3+
- Python with `python-docx` and `lxml` (`requirements.txt`)
- LaTeX/BibTeX
- Desktop Word for the **user** to open, update fields, and (if live) refresh Zotero
- For live citations: Zotero, Word plugin, Better BibTeX, official `zotero.lua`
- Optional: `scripts/validate_with_word.ps1` (Windows COM) — agent may offer it and run it **only if the user asks**

Static CSL works without Zotero/BBT.

## Related projects

Not dependencies — useful context when extending this skill. Summary: [`latex-to-word-workflow/references/ecosystem-notes.md`](latex-to-word-workflow/references/ecosystem-notes.md).

| Project | Overlap |
|---|---|
| [adamsconchallos/tex2docx](https://github.com/adamsconchallos/tex2docx) | Flatten + fidelity counts + PDF figure handling |
| [jay-dennis/tex2docx](https://github.com/jay-dennis/tex2docx) | TeX prep, label prefixes, pandoc-xnos era workflow |
| [tianbaiting/tex2doc](https://github.com/tianbaiting/tex2doc) | PDF image conversion for Word |
| [scavero/tex2docx](https://github.com/scavero/tex2docx) | TikZ/cover rasterization, reference-doc |
| [xhan97/Latex2WordExample](https://github.com/xhan97/Latex2WordExample) | pandoc-crossref + citeproc example |
| [lierdakil/pandoc-crossref](https://github.com/lierdakil/pandoc-crossref) | Filter-based cross-refs (static; different from SEQ/REF promote) |
| [retorquere/zotero-better-bibtex](https://github.com/retorquere/zotero-better-bibtex) | Official `zotero.lua` live fields |
| [jyluo1994/zotero-word-citation](https://github.com/jyluo1994/zotero-word-citation) | Agent skill for Zotero→Word citation routes |

This repo’s niche: **agent skill** + live **or** static cites + **native Word SEQ/REF** + package audits + **user** Word acceptance.

## License

MIT. See [LICENSE](LICENSE).

## Community

- [LINUX DO](https://linux.do/)
