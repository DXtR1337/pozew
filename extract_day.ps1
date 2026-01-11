# extract_day.ps1
# Wyciąga wszystkie wiadomości z danego dnia z found_medical_messages.json
# Uzycie: .\extract_day.ps1 -Date "2023-04-06"

param(
    [Parameter(Mandatory = $true)]
    [string]$Date
)

$JsonPath = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\found_medical_messages.json"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WIADOMOSCI Z DNIA: $Date" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$Data = Get-Content -Path $JsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($Data.by_date.PSObject.Properties.Name -contains $Date) {
    $Messages = $Data.by_date.$Date
    Write-Host "Znaleziono $($Messages.Count) wiadomosci" -ForegroundColor Green
    Write-Host ""
    Write-Host "| Godz | Nadawca | Tresc | Watek | Slowa kluczowe |"
    Write-Host "|:-----|:--------|:------|:------|:---------------|"
    
    foreach ($Msg in $Messages) {
        $ContentShort = $Msg.content
        if ($ContentShort.Length -gt 80) {
            $ContentShort = $ContentShort.Substring(0, 80) + "..."
        }
        $ContentShort = $ContentShort -replace "`n", " " -replace "\|", "-"
        Write-Host "| $($Msg.time) | $($Msg.sender) | $ContentShort | $($Msg.thread) | $($Msg.keywords) |"
    }
}
else {
    Write-Host "Brak wiadomosci dla daty: $Date" -ForegroundColor Red
    Write-Host ""
    Write-Host "Dostepne daty:" -ForegroundColor Yellow
    $Data.by_date.PSObject.Properties.Name | Sort-Object | ForEach-Object { Write-Host "  $_" }
}
