# extract_all_day.ps1
# Wyciaga WSZYSTKIE wiadomosci z pełnej bazy dla danego dnia
param([string]$Date = "2023-04-02")

$JsonPath = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\messenger_daily_summary_all.json"
$Data = Get-Content -Path $JsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

Write-Host "========================================"
Write-Host "PELNA BAZA - DZIEN: $Date"
Write-Host "========================================"
Write-Host ""

if ($Data.PSObject.Properties.Name -contains $Date) {
    $Messages = $Data.$Date
    Write-Host "Znaleziono: $($Messages.Count) wiadomosci"
    Write-Host ""
    
    foreach ($Msg in $Messages) {
        $Content = $Msg.content -replace "`n", " "
        if ($Content.Length -gt 150) { $Content = $Content.Substring(0, 150) + "..." }
        Write-Host "$($Msg.time) [$($Msg.sender)] $Content"
        Write-Host "   -> Watek: $($Msg.source)"
        Write-Host ""
    }
}
else {
    Write-Host "Brak wiadomosci dla: $Date"
}
