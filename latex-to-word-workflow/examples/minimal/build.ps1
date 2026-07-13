param(
    [ValidateSet('Static', 'ZoteroLive')]
    [string]$Mode = 'Static',
    [string]$Csl,
    [string]$ZoteroLua,
    [string]$ReferenceDoc = '..\..\assets\reference.docx'
)

$ErrorActionPreference = 'Stop'
$output = Join-Path $PSScriptRoot 'output'
New-Item -ItemType Directory -Force -Path $output | Out-Null

if ($Mode -eq 'Static') {
    if (-not $Csl) { throw 'Static mode requires -Csl path\to\journal.csl' }
    pandoc "$PSScriptRoot\main.tex" -f latex -t docx --wrap=none --citeproc `
        "--bibliography=$PSScriptRoot\references.bib" "--csl=$Csl" `
        "--reference-doc=$PSScriptRoot\$ReferenceDoc" `
        -o "$output\minimal_static.docx"
    if ($LASTEXITCODE -ne 0) { throw "Pandoc failed with exit code $LASTEXITCODE" }
}
else {
    if (-not $ZoteroLua) { throw 'ZoteroLive mode requires -ZoteroLua path\to\zotero.lua' }
    $env:NO_PROXY = '*'
    $env:no_proxy = '*'
    Write-Warning 'Replace exampleCitation2025 in main.tex and references.bib with a citation key present in your Better BibTeX library.'
    pandoc "$PSScriptRoot\main.tex" -f latex -t docx --wrap=none `
        "--lua-filter=$ZoteroLua" "--reference-doc=$PSScriptRoot\$ReferenceDoc" `
        -o "$output\minimal_zotero_live.docx"
    if ($LASTEXITCODE -ne 0) { throw "Pandoc failed with exit code $LASTEXITCODE" }
}
