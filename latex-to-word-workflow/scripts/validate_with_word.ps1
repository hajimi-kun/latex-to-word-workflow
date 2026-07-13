param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$resolved = (Resolve-Path -LiteralPath $Path).Path
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.OpenNoRepairDialog($resolved, $false, $true)
    $zotero = 0
    foreach ($field in @($doc.Fields)) {
        if ($field.Code.Text -like '*ZOTERO_ITEM CSL_CITATION*') { $zotero++ }
    }
    [pscustomobject]@{
        open_no_repair = $true
        pages = $doc.ComputeStatistics(2)
        fields = $doc.Fields.Count
        zotero_citation_fields = $zotero
    } | ConvertTo-Json
}
finally {
    if ($doc) { $doc.Close($false) | Out-Null }
    if ($word) { $word.Quit() | Out-Null }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
