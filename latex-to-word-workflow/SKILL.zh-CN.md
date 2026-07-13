# LaTeX 转精美 Word，并支持 Zotero 动态引文

本文件是 `SKILL.md` 的中文版，供中文阅读和分享使用。兼容 Agent Skills 的工具通常以 `SKILL.md` 作为标准入口。

## 内置资源

- `assets/reference.docx`：带可见样张的通用 A4 Word 样式模板。
- `scripts/test_better_bibtex.py`：测试本地 Better BibTeX 并检索 Zotero 条目。
- `scripts/check_citation_keys.py`：核对 `\cite{...}`、BibTeX 和 Better BibTeX key。
- `scripts/format_generated_docx.py`：映射图片、题注、表格和参考文献 Word 样式。
- `scripts/validate_docx.py`：检查 DOCX relationship、内容数量和 Zotero 字段。
- `scripts/validate_with_word.ps1`：验证 Microsoft Word 无修复打开。
- `examples/minimal/`：最小静态/动态构建示例；Zotero 动态模式前需替换示例 citation key。
- `references/first-run-setup.md`：首次使用时的环境、Word 模板、Zotero 和最小测试配置指南。

## 首次使用判断

转换完整稿件前，先判断当前环境是否已经完成初始化配置。如果以下任一事项不明确，则视为尚未配置：

- Pandoc、安装了 `python-docx` 的 Python、LaTeX/BibTeX 或 Microsoft Word 是否可用。
- 项目 Word 参考模板的位置，以及作者是否已经确认其样式。
- 使用 Zotero 动态模式时，Zotero、Word 插件、Better BibTeX 和官方 `zotero.lua` 是否可用。
- 是否已有一个只包含一条真实引文的 Zotero 动态 DOCX 通过 Word 和 Zotero 验证。

环境尚未配置时，必须完整读取 `references/first-run-setup.md`，完成其中的配置和最小测试后，才能转换完整稿件。先自动检测已有组件，用直白语言报告已安装项和缺失项；安装软件或插件前，应先取得用户确认。

环境已经配置时，直接执行日常流程：核对 citation key → 编译 LaTeX → 生成 DOCX → 映射 Word 样式 → 验证 → 在 Word 中刷新引文并生成参考文献目录。

## 选择引用模式

- **Zotero 动态模式（适合作者继续编辑）：** 使用 Better BibTeX 官方 `zotero.lua` 生成原生 `ADDIN ZOTERO_ITEM CSL_CITATION` 字段。可在 Word 中使用 Zotero 的 `Refresh`、`Document Preferences` 和 `Add/Edit Bibliography`。
- **静态 CSL 模式（备用或预览）：** 使用 Pandoc 的 `--citeproc --bibliography --csl`。引文和参考文献是可编辑文本，不是 Zotero 动态字段。

同一次构建中不要同时使用 `--citeproc` 和 `zotero.lua`。

## 所需配置

通用配置：

- Pandoc 3+、LaTeX/BibTeX、安装了 `python-docx` 的 Python，以及 Windows 版 Microsoft Word。
- 完整的 LaTeX 入口文件，并将全部图片目录加入 `--resource-path`。
- 一个以样式为主的 `reference.docx`，用于定义页面、字体、标题、题注、表格和参考文献格式。
- 用于保存生成 DOCX 的输出目录。

Zotero 动态模式还需要：

- 运行中的 Zotero 桌面端、Zotero Word 插件和 Better BibTeX。
- 从 `https://retorque.re/zotero-better-bibtex/exporting/zotero.lua` 下载当前官方过滤器。
- 在 Zotero、`references.bib` 和所有 `\cite{key}` 中统一使用 Better BibTeX citation key。
- 检查本地接口 `http://127.0.0.1:23119/better-bibtex/json-rpc`。如果本机代理拦截 localhost，设置 `NO_PROXY=*`；返回 404 通常表示 Better BibTeX 未安装或未启用。

## 转换前检查

1. 检查 LaTeX 入口、参考文献库、图片、Word 模板和输出路径。
2. 使用 BibTeX 编译 LaTeX，并在出现错误时停止：

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

3. 确认每个被引用的 key 都存在于 `references.bib`。
4. 使用 Zotero 动态模式时，先通过 Better BibTeX 解析全部 key。根据 DOI 或题名进行匹配，拒绝缺失或存在歧义的结果，不要猜测 citation key。
5. 使用 Word `Documents.OpenNoRepairDialog` 验证 reference DOCX 可以正常打开。

有内置脚本时，使用：

```powershell
python scripts/test_better_bibtex.py "citationKeyOrTitle"
python scripts/check_citation_keys.py --tex main.tex section*.tex --bib references.bib
```

## 生成 Zotero 动态 DOCX

该模式不要使用 `--citeproc`：

```powershell
$env:NO_PROXY = "*"
$env:no_proxy = "*"

pandoc main.tex `
  -f latex `
  -t docx `
  --wrap=none `
  --lua-filter="path\to\zotero.lua" `
  "--resource-path=.;..;..\figures" `
  --reference-doc="path\to\reference.docx" `
  -o "output\manuscript_zotero_live.docx"
```

过滤器会生成动态引文字段，但通常不会自动插入参考文献目录字段。打开生成的 Word，在 Zotero `Document Preferences` 中选择期刊格式，点击 `Refresh`，将光标放到 `References` 标题下，再点击 `Add/Edit Bibliography`。

## 生成静态 CSL DOCX

当 Zotero 或 Better BibTeX 不可用，或者需要确定性的预览文件时，使用此模式：

```powershell
pandoc main.tex `
  -f latex `
  -t docx `
  --wrap=none `
  --citeproc `
  --bibliography="references.bib" `
  --csl="path\to\journal.csl" `
  --metadata "reference-section-title=References" `
  "--resource-path=.;..;..\figures" `
  --reference-doc="path\to\reference.docx" `
  -o "output\manuscript_static.docx"
```

## Word 模板与样式映射

由 `reference.docx` 定义外观，再通过后处理程序分配语义样式，但不要重写段落文字：

| 内容 | Word 样式 |
|---|---|
| 论文正文 | `Body Text` |
| 仅包含图片的段落 | `Figure`（居中、首行缩进为 0） |
| 图题和表题 | `Caption` |
| 表格单元格文字 | `Table Body` |
| 参考文献 | `Bibliography`（悬挂缩进） |
| 章节标题 | `Heading 1/2/3` |

只使用 `python-docx` 修改段落或文字运行样式、页面设置和图片尺寸。不要替换包含引文字段的段落文本。模板负责定义样式，但 Pandoc 不一定会自动分配自定义的 `Figure` 或 `Table Body` 样式，需要在转换后进行映射。

```powershell
python scripts/format_generated_docx.py output.docx
```

## DOCX 完整性规则

- 生成一个完整的新 DOCX，不要将原始段落 XML 拼接到现有 DOCX 包中。
- 复制 XML 节点时不能丢失其 relationship；超链接或媒体关系缺失会导致 Word 报告文件损坏。
- 只有在 Zotero 一对一匹配成功后才能迁移 citation key；同时更新 `references.bib` 条目 key 和所有 `\cite{...}`，然后重新编译 LaTeX。
- 同时生成 Zotero 动态版和静态 CSL 版时，使用不同文件名。

## 验收检查

只有完成所有适用检查后才能接受输出：

1. LaTeX/BibTeX 编译成功，并且没有未定义引用。
2. DOCX ZIP 可以打开，所有 `r:id`、`r:embed` 和 `r:link` 都在相应 relationship 文件中有定义。
3. 使用 `python-docx` 检查段落、表格和图片数量。不要根据其纯文本提取结果判断 Word 公式是否正确。
4. Zotero 动态版 XML 中包含预期数量的 `ADDIN ZOTERO_ITEM CSL_CITATION` 和预期 Zotero item key。
5. Microsoft Word `Documents.OpenNoRepairDialog` 可以正常打开文件。ZIP 有效或 `python-docx` 能读取并不足以证明 Word 无需修复。
6. 在 Word 中点击 Zotero `Refresh` 成功，`Add/Edit Bibliography` 能按所选期刊格式生成参考文献目录。
7. 目视检查公式、图片位置、题注、表格、引文、参考文献、分页和交叉引用。

```powershell
python scripts/validate_docx.py output.docx --expect-zotero 3
powershell -File scripts/validate_with_word.ps1 -Path output.docx
```

## 已知边界

- Zotero 动态字段在构建时需要 Zotero 和 Better BibTeX；静态 CSL 模式不需要。
- Zotero 引文可以动态更新，但 Pandoc 的图表交叉引用通常仍是静态超链接，除非项目额外生成 Word 字段。
- 参考文献内容格式由 Zotero CSL 控制；段落外观仍可能继承相应的 Word 样式。
