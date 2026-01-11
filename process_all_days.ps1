# process_all_days.ps1
# Przetwarza WSZYSTKIE dni i zapisuje wyniki do plikow

$JsonPath = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\messenger_daily_summary_all.json"
$OutputDir = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\extracted_days"

if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir }

$Data = Get-Content -Path $JsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

$Dates = $Data.PSObject.Properties.Name | Sort-Object

Write-Host "Przetwarzam $($Dates.Count) dni..." -ForegroundColor Cyan

foreach ($Date in $Dates) {
    $Messages = $Data.$Date
    $OutputFile = Join-Path $OutputDir "$Date.txt"
    
    $Lines = @()
    $Lines += "# WIADOMOSCI Z DNIA: $Date"
    $Lines += "# Liczba: $($Messages.Count)"
    $Lines += ""
    $Lines += "| Godz | Nadawca | Tresc | Watek |"
    $Lines += "|:-----|:--------|:------|:------|"
    
    foreach ($Msg in $Messages) {
        $Content = $Msg.content -replace "`n", " " -replace "\|", "-"
        if ($Content.Length -gt 100) { $Content = $Content.Substring(0, 100) + "..." }
        $Source = $Msg.source -replace ".*\\", ""
        $Lines += "| $($Msg.time) | $($Msg.sender) | $Content | $Source |"
    }
    
    $Lines -join "`n" | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Host "OK: $Date ($($Messages.Count) wiadomosci)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Gotowe! Pliki w: $OutputDir" -ForegroundColor Yellow
