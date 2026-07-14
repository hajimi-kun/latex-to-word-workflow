# LaTeX → Word（可选 Zotero）

本文件是 `SKILL.md` 的中文对照。兼容 Agent Skills 的工具以 `SKILL.md` 为标准入口。

## 资源

| 路径 | 作用 |
|---|---|
| `assets/reference.docx` | 通用 A4 模板（复制到项目再改，勿直接改仓库内资产） |
| `scripts/*.py` | 审计、样式、原生交叉引用、包结构检查 |
| `scripts/validate_with_word.ps1` | 可选 Windows COM 打开探测 — **仅当用户要求时** |
| `examples/minimal/` | 最小示例（Zotero 动态模式前替换示例 citation） |
| `references/first-run-setup.md` | 环境检测、模板、冒烟测试 |
| `references/cross-references.md` | 完整入口、SEQ/REF 提升、编号边界 |
| `references/ecosystem-notes.md` | 同类项目（扩展时再读） |
| `requirements.txt` | `python-docx`、`lxml` |

## 模式（二选一）

- **Zotero 动态：** 仅 Pandoc + 官方 `zotero.lua`，不要 `--citeproc`。**用户**在 Word 中完成 prefs → Refresh → 参考文献。
- **静态 CSL：** `--citeproc --bibliography --csl`。

不要在同一次构建中混用 `--citeproc` 与 `zotero.lua`。

## 平台

| 能力 | 说明 |
|---|---|
| Agent 构建与包检查 | Pandoc 3+、Python + `requirements.txt`、LaTeX/BibTeX，跨 OS |
| Word / Zotero 界面 | 默认由**用户**打开 DOCX（F9、Zotero Refresh、目视） |
| Word COM | **可选。** 可向用户说明；仅当用户要求且 Windows 有 Word 时再跑 `validate_with_word.ps1` |
| 构建时动态 Zotero | 需运行中的 Zotero + BBT；过滤器：https://retorque.re/zotero-better-bibtex/exporting/zotero.lua |
| 本地 BBT API | `http://127.0.0.1:23119/better-bibtex/json-rpc`；代理干扰 localhost 时再设 `NO_PROXY=*` |

环境未确认时，先完整完成 `references/first-run-setup.md`。先检测，安装前征得用户同意。

## 日常流程

1. **源文件预检**
   - 完整入口；标签建议 `fig:` / `tab:` / `eq:`。
   - **图片：** Word 不能嵌 PDF。必须把 `\includegraphics` 改成 PNG/JPEG；旁边放同主名 `.png` **不会**自动替换 `figure.pdf`。
   - 需要交叉引用的编号对象尽量都带 label；提升器按 LaTeX 计数顺序编号（无 label 的编号对象仍占号）。
   - 核对 key：

```text
python scripts/check_citation_keys.py --tex main.tex --bib references.bib --skip-zotero
python scripts/check_citation_keys.py --tex main.tex --bib references.bib
```

2. **编译 LaTeX**（含 BibTeX），出错即停。

3. **Pandoc 转换完整入口**。`--resource-path` 填实际图片目录。

```text
# 静态
pandoc main.tex -f latex -t docx --wrap=none --citeproc --bibliography=references.bib --csl=journal.csl --metadata reference-section-title=References --resource-path=.;figures --reference-doc=reference.docx -o out/static.docx

# Zotero 动态（勿加 --citeproc）。可选：--metadata zotero_csl_style=apa
pandoc main.tex -f latex -t docx --wrap=none --lua-filter=zotero.lua --resource-path=.;figures --reference-doc=reference.docx -o out/zotero_live.docx
```

不要用 `pandoc-crossref` 替代本 skill 的原生 SEQ/REF 提升。

4. **样式 → 原生交叉引用**（每次重建只提升一次）：

```text
python scripts/format_generated_docx.py out/doc.docx
python scripts/promote_native_crossrefs.py out/doc.docx out/doc_native.docx --tex main.tex
```

5. **Agent 包检查**（默认不操作 Word；用户要求 COM 时除外）：

```text
python scripts/validate_docx.py out/doc_native.docx --tex main.tex --expect-zotero N
python scripts/check_cross_references.py --tex main.tex --docx out/doc_native.docx --require-native-word-fields
```

- 静态 CSL 可省略 `--expect-zotero`。可选 `--expect-zotero-keys key1 key2` 校验字段 JSON 内的 BBT key。
- 带 `--tex` 时默认**强制**源表/图数量与 DOCX 一致；诊断可用 `--no-enforce-tex-counts`。显式 `.pdf` 插图默认失败（除非 `--allow-pdf-figures`）。
- `REF` 目标书签必须存在；重复书签名失败。
- 残留 `[@...]` 失败。脚本通过 ≠ 可交付。

6. **用户在 Word 中验收** — 告知 DOCX 路径，请用户：

- 打开（无修复提示）。动态稿若首次误报损坏，可重建一次。
- **动态模式：先** Document Preferences 选样式并确定，**再** Refresh，然后 Add/Edit Bibliography。
- 全选 → **F9**。
- 对照 PDF 抽查公式、图、题注、表、引文、参考文献、分页。

若**用户要求** Windows 自动打开检查：

```text
powershell -File scripts/validate_with_word.ps1 -Path out/doc_native.docx
```

默认不要跑 COM；不要代点 Zotero。

## 样式映射

| 内容 | 样式 |
|---|---|
| 正文 | `Body Text` |
| 仅图片段 | `Figure` |
| 题注 | `Caption` |
| 表内文字 | `Table Body` |
| 参考文献列表 | `Bibliography` |

只改样式，不改写含 Zotero 域的 run。标题识别：`References`、`Bibliography`、`参考文献`、`引用文献`。

## 硬性规则

- 生成完整新 DOCX；勿丢失 relationship 拼接 XML。
- Zotero / bib / `\cite` 统一 BBT key；禁止猜测 key。
- 跨文件引用必须完整入口；样式后处理后再审计。
- 缺图/仅 PDF 图：修后再接受构建。

## 边界

- 动态模式构建时需要 BBT；静态不需要。
- 勿对同一 DOCX 反复 promote。
- 公式提升需 `--tex`，display math 与 OMML 数量一致。
- 编号按 LaTeX 环境顺序（非 star 的 figure/table/equation/align 等）；无 label 的编号公式仍占号，故其后有 label 的可为 Eq. (2)。复杂版式对照 PDF。
- 题注需 Caption 样式或 Fig./Table/图/表 前缀，否则提升失败。
- Pandoc 可能忽略 `\setcounter`。
- Agent 验收以结构脚本为主；最终以用户 Word 检查为准（COM 仅应要求时）。
- bib 审计较简，复杂库需人工核对。
