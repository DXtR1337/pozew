
$basePath = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\your_facebook_activity\messages\inbox"
$outputFile = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\messenger_daily_summary_all.json"

$startDate = Get-Date "2023-04-01"
$endDate = Get-Date "2023-06-30"

$dailyMessages = @{}

$jsonFiles = Get-ChildItem -Path $basePath -Filter "*.json" -Recurse

foreach ($file in $jsonFiles) {
    try {
        $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
        $relPath = $file.FullName.Replace($basePath + "\", "")
        
        if ($content.messages) {
            foreach ($msg in $content.messages) {
                if ($msg.timestamp_ms) {
                    $dt = [datetimeOffset]::FromUnixTimeMilliseconds($msg.timestamp_ms).DateTime
                    if ($dt -ge $startDate -and $dt -le $endDate) {
                        $dateStr = $dt.ToString("yyyy-MM-dd")
                        
                        if (-not $dailyMessages.ContainsKey($dateStr)) {
                            $dailyMessages[$dateStr] = New-Object System.Collections.Generic.List[PSObject]
                        }
                        
                        $text = $msg.content
                        if (-not $text) {
                            if ($msg.photos) { $text = "[Photo: " + $msg.photos.Count + "]" }
                            elseif ($msg.videos) { $text = "[Video: " + $msg.videos.Count + "]" }
                            elseif ($msg.files) { $text = "[File: " + $msg.files.Count + "]" }
                            elseif ($msg.sticker) { $text = "[Sticker]" }
                            else { $text = "[No text content]" }
                        }
                        
                        # Decipher Polish characters (Messenger exports often have escaped sequences)
                        # Actually standard JSON decode should handle it, but sometimes it doesn't.
                        # We'll see.
                        
                        $dailyMessages[$dateStr].Add(@{
                            time = $dt.ToString("HH:mm:ss")
                            sender = $msg.sender_name
                            content = $text
                            source = $relPath
                            ts = $msg.timestamp_ms
                        })
                    }
                }
            }
        }
    } catch {
        Write-Host "Error processing $($file.FullName): $_"
    }
}

# Sort and output
$finalData = @{}
foreach ($date in $dailyMessages.Keys) {
    $finalData[$date] = $dailyMessages[$date] | Sort-Object ts
}

$finalData | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding utf8
Write-Host "Extraction complete. Saved to $outputFile."
