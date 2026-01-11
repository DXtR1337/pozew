
$basePath = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\your_facebook_activity\messages\inbox"
$outputFile = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\MEDYCZNA_LINIA_CZASU_MESSENGER.md"

$relevantThreads = @(
    "kacperdrewniak_2173539216268086",
    "bogusiaptak_3139495316380919",
    "9052962828108059",
    "dziwniludzie_6103258886383503"
)

$allMessages = New-Object System.Collections.Generic.List[PSObject]

function Decode-MessengerText($text) {
    if (-not $text) { return "" }
    try {
        $bytes = [System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($text)
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    }
    catch {
        return $text
    }
}

foreach ($folder in $relevantThreads) {
    $path = Join-Path $basePath $folder
    if (-not (Test-Path $path)) { continue }
    
    $files = Get-ChildItem -Path $path -Filter "message_*.json"
    foreach ($file in $files) {
        $data = Get-Content $file.FullName -Raw | ConvertFrom-Json
        $threadTitle = Decode-MessengerText $data.title
        
        foreach ($msg in $data.messages) {
            if (-not $msg.timestamp_ms) { continue }
            $dt = [datetimeOffset]::FromUnixTimeMilliseconds($msg.timestamp_ms).DateTime
            
            if ($dt.Year -eq 2023 -and ($dt.Month -ge 4 -and $dt.Month -le 6)) {
                $content = Decode-MessengerText $msg.content
                if (-not $content) {
                    if ($msg.photos) { $content = "[Zdjęcie: " + $msg.photos.Count + "]" }
                    elseif ($msg.videos) { $content = "[Wideo: " + $msg.videos.Count + "]" }
                    elseif ($msg.sticker) { $content = "[Naklejka]" }
                    else { $content = "[Inna zawartość]" }
                }
                
                $sender = Decode-MessengerText $msg.sender_name
                
                $allMessages.Add(@{
                        ts      = $msg.timestamp_ms
                        dt_str  = $dt.ToString("yyyy-MM-dd HH:mm:ss")
                        date    = $dt.ToString("yyyy-MM-dd")
                        sender  = $sender
                        content = $content
                        thread  = $threadTitle
                    })
            }
        }
    }
}

$sorted = $allMessages | Sort-Object ts

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("# Medyczna Linia Czasu - Messenger (Wyselekcjonowane wątki)")
[void]$sb.AppendLine("Wątki: Kacper Drewniak, Bogusia Ptak, Grupa (Radek, Julita...), Dziwni Ludzie")
[void]$sb.AppendLine("")

$currentDate = ""
foreach ($msg in $sorted) {
    if ($msg.date -ne $currentDate) {
        $currentDate = $msg.date
        [void]$sb.AppendLine("## $currentDate")
        [void]$sb.AppendLine("")
    }
    [void]$sb.AppendLine("- **[$($msg.dt_str)] $($msg.sender)** ($($msg.thread)): $($msg.content)")
}

$sb.ToString() | Out-File -FilePath $outputFile -Encoding utf8
Write-Host "Timeline saved to $outputFile"
