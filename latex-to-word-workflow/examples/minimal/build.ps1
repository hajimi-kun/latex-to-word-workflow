param(
    [ValidateSet('Static', 'ZoteroLive')]
    [string]$Mode = 'Static',
    [string]$Csl,
    [string]$ZoteroLua,
    [string]$ReferenceDoc
)

$ErrorActionPreference = 'Stop'
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$scripts = Join-Path $skillRoot 'scripts'
$output = Join-Path $PSScriptRoot 'output'
New-Item -ItemType Directory -Force -Path $output | Out-Null

if (-not $ReferenceDoc) {
    $ReferenceDoc = Join-Path $skillRoot 'assets\reference.docx'
}
elseif (-not [IO.Path]::IsPathRooted($ReferenceDoc)) {
    $candidates = @(
        (Join-Path $PSScriptRoot $ReferenceDoc),
        (Join-Path $skillRoot $ReferenceDoc)
    )
    $resolved = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $resolved) { throw "reference.docx not found: $ReferenceDoc" }
    $ReferenceDoc = (Resolve-Path -LiteralPath $resolved).Path
}
else {
    $ReferenceDoc = (Resolve-Path -LiteralPath $ReferenceDoc).Path
}

if ($Mode -eq 'Static') {
    if (-not $Csl) {
        throw 'Static mode requires -Csl path/to/journal.csl (e.g. from https://github.com/citation-style-language/styles)'
    }
    $built = Join-Path $output 'minimal_static.docx'
    pandoc (Join-Path $PSScriptRoot 'main.tex') -f latex -t docx --wrap=none --citeproc `
        "--bibliography=$(Join-Path $PSScriptRoot 'references.bib')" "--csl=$Csl" `
        "--resource-path=$PSScriptRoot" "--reference-doc=$ReferenceDoc" `
        -o $built
    if ($LASTEXITCODE -ne 0) { throw "Pandoc failed with exit code $LASTEXITCODE" }
}
else {
    if (-not $ZoteroLua) { throw 'ZoteroLive mode requires -ZoteroLua path/to/zotero.lua' }
    Write-Warning 'Replace exampleCitation2025 in main.tex and references.bib with a citation key present in your Better BibTeX library.'
    # Only needed when a system proxy intercepts localhost BBT calls
    $env:NO_PROXY = '*'
    $env:no_proxy = '*'
    $built = Join-Path $output 'minimal_zotero_live.docx'
    pandoc (Join-Path $PSScriptRoot 'main.tex') -f latex -t docx --wrap=none `
        "--lua-filter=$ZoteroLua" "--resource-path=$PSScriptRoot" "--reference-doc=$ReferenceDoc" `
        -o $built
    if ($LASTEXITCODE -ne 0) { throw "Pandoc failed with exit code $LASTEXITCODE" }
}

$native = [IO.Path]::Combine($output, ([IO.Path]::GetFileNameWithoutExtension($built) + '_native.docx'))
python (Join-Path $scripts 'format_generated_docx.py') $built
if ($LASTEXITCODE -ne 0) { throw "Style mapping failed with exit code $LASTEXITCODE" }
python (Join-Path $scripts 'promote_native_crossrefs.py') $built $native --tex (Join-Path $PSScriptRoot 'main.tex')
if ($LASTEXITCODE -ne 0) { throw "Native cross-reference promotion failed with exit code $LASTEXITCODE" }
python (Join-Path $scripts 'check_cross_references.py') --tex (Join-Path $PSScriptRoot 'main.tex') --docx $native --require-native-word-fields
if ($LASTEXITCODE -ne 0) { throw "Cross-reference validation failed with exit code $LASTEXITCODE" }
$validateArgs = @(
    (Join-Path $scripts 'validate_docx.py'),
    $native,
    '--tex', (Join-Path $PSScriptRoot 'main.tex')
)
if ($Mode -eq 'ZoteroLive') {
    # After replacing exampleCitation2025 with a real BBT key, pass that key here if desired:
    # $validateArgs += @('--expect-zotero-keys', 'yourRealKey')
    $validateArgs += @('--expect-zotero', '1')
}
python @validateArgs
if ($LASTEXITCODE -ne 0) { throw "DOCX validation failed with exit code $LASTEXITCODE" }
Write-Host "Built: $native"
