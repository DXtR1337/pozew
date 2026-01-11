param(
    [string]$startDateStr = "2023-05-06",
    [string]$endDateStr = "2023-05-14"
)

$startDate = Get-Date $startDateStr
$endDate = Get-Date $endDateStr
$path = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\messenger_daily_summary_all.json"
$outFile = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\temp_extraction.txt"

if (-not (Test-Path $path)) {
    Write-Host "JSON file not found."
    exit
}

$json = Get-Content $path -Raw | ConvertFrom-Json
$output = @()

$currentDate = $startDate
while ($currentDate -le $endDate) {
    $dateStr = $currentDate.ToString("yyyy-MM-dd")
    $output += "## $dateStr"
    
    if ($json.$dateStr) {
        $messages = $json.$dateStr
        foreach ($msg in $messages) {
            # Filter for key people or just dump everything?
            # Dumping everything is safer to find context, user wanted "kazdy dzien"
            $line = "[$($msg.time)] [$($msg.sender)]: $($msg.content)"
            $output += $line
        }
    }
    else {
        $output += "No messages found."
    }
    $output += ""
    $currentDate = $currentDate.AddDays(1)
}

$output | Out-File -FilePath $outFile -Encoding utf8
Write-Host "Extraction complete for $startDateStr to $endDateStr"
