# search_all_threads.ps1
# Przeszukuje WSZYSTKIE watki Messenger

$BasePath = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\your_facebook_activity\messages\inbox"
$OutputJson = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\found_medical_messages.json"
$OutputMd = "c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\found_threads_summary.md"

$StartDate = Get-Date "2023-04-01"
$EndDate = Get-Date "2023-06-30 23:59:59"

# Slowa kluczowe medyczne i dowodowe
$AllKeywords = @(
    'bol'
    'boli'
    'bolalo'
    'cierpie'
    'cierpienie'
    'szpital'
    'lekarz'
    'doktor'
    'pielegniarka'
    'ordynator'
    'operacja'
    'zabieg'
    'dren'
    'drenaz'
    'saczek'
    'opatrunek'
    'znieczulenie'
    'narkoza'
    'ropien'
    'przetoka'
    'crohn'
    'zapalenie'
    'infekcja'
    'bakteria'
    'sepsa'
    'zakazenie'
    'tomografia'
    'rtg'
    'usg'
    'badanie'
    'wynik'
    'posiew'
    'glod'
    'glodny'
    'jedzenie'
    'dieta'
    'nutri'
    'nie jem'
    'zaglodza'
    'zalamanie'
    'psycholog'
    'placze'
    'nie moge'
    'strach'
    'antybiotyk'
    'ibuprofen'
    'morfina'
    'lek'
    'leki'
    'kroplowka'
    'goraczka'
    'krew'
    'ropa'
    'wydzielina'
    'wyciek'
    'temperatura'
    'nie przyszedl'
    'czekam'
    'nikt nie'
    'ignoruja'
    'blad'
    'pomylka'
    'zaniedbanie'
    'za pozno'
)

Write-Host "Rozpoczynam przeszukiwanie watkow Messenger..." -ForegroundColor Cyan
Write-Host "Okres: $($StartDate.ToString('yyyy-MM-dd')) do $($EndDate.ToString('yyyy-MM-dd'))"
Write-Host "Slow kluczowych: $($AllKeywords.Count)"
Write-Host ""

$AllMessages = @()
$ThreadsWithHits = @{}
$Threads = Get-ChildItem -Path $BasePath -Directory

Write-Host "Znaleziono $($Threads.Count) watkow do przeszukania"
Write-Host ""

foreach ($ThreadDir in $Threads) {
    $ThreadMessages = @()
    $JsonFiles = Get-ChildItem -Path $ThreadDir.FullName -Filter "message_*.json" -ErrorAction SilentlyContinue
    
    foreach ($JsonFile in $JsonFiles) {
        try {
            $RawContent = Get-Content -Path $JsonFile.FullName -Raw -Encoding UTF8
            $Data = $RawContent | ConvertFrom-Json
            $ThreadTitle = $Data.title
            
            foreach ($Msg in $Data.messages) {
                if (-not $Msg.timestamp_ms) { continue }
                
                $UnixEpoch = Get-Date "1970-01-01 00:00:00"
                $MsgDateTime = $UnixEpoch.AddMilliseconds($Msg.timestamp_ms).ToLocalTime()
                
                if ($MsgDateTime -lt $StartDate -or $MsgDateTime -gt $EndDate) { continue }
                
                $Content = $Msg.content
                if (-not $Content) { continue }
                
                $FoundKeywords = @()
                foreach ($Kw in $AllKeywords) {
                    if ($Content -imatch [regex]::Escape($Kw)) {
                        $FoundKeywords += $Kw
                    }
                }
                
                if ($FoundKeywords.Count -gt 0) {
                    $ThreadMessages += [PSCustomObject]@{
                        timestamp = $Msg.timestamp_ms
                        datetime  = $MsgDateTime.ToString('yyyy-MM-dd HH:mm:ss')
                        date      = $MsgDateTime.ToString('yyyy-MM-dd')
                        time      = $MsgDateTime.ToString('HH:mm')
                        sender    = $Msg.sender_name
                        content   = $Content
                        thread    = $ThreadTitle
                        thread_id = $ThreadDir.Name
                        keywords  = ($FoundKeywords | Select-Object -Unique) -join ", "
                    }
                }
            }
        }
        catch {
            Write-Host "Blad w $($JsonFile.Name): $_" -ForegroundColor Yellow
        }
    }
    
    if ($ThreadMessages.Count -gt 0) {
        $AllMessages += $ThreadMessages
        $ThreadsWithHits[$ThreadDir.Name] = $ThreadMessages.Count
        Write-Host "OK $($ThreadDir.Name): $($ThreadMessages.Count) wiadomosci" -ForegroundColor Green
    }
}

$AllMessages = $AllMessages | Sort-Object timestamp

$DailyMessages = @{}
foreach ($Msg in $AllMessages) {
    if (-not $DailyMessages.ContainsKey($Msg.date)) {
        $DailyMessages[$Msg.date] = @()
    }
    $DailyMessages[$Msg.date] += $Msg
}

$OutputData = @{
    metadata        = @{
        generated         = (Get-Date).ToString('o')
        period            = "$($StartDate.ToString('yyyy-MM-dd')) - $($EndDate.ToString('yyyy-MM-dd'))"
        keywords_count    = $AllKeywords.Count
        total_messages    = $AllMessages.Count
        threads_searched  = $Threads.Count
        threads_with_hits = $ThreadsWithHits.Count
    }
    by_date         = $DailyMessages
    threads_summary = $ThreadsWithHits
}

$OutputData | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputJson -Encoding UTF8

$MdLines = @()
$MdLines += "# Wyniki Przeszukania Wszystkich Watkow Messenger"
$MdLines += ""
$MdLines += "Wygenerowano: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
$MdLines += ""
$MdLines += "Okres: $($StartDate.ToString('yyyy-MM-dd')) do $($EndDate.ToString('yyyy-MM-dd'))"
$MdLines += ""
$MdLines += "Watkow przeszukanych: $($Threads.Count)"
$MdLines += ""
$MdLines += "Watkow z trafieniami: $($ThreadsWithHits.Count)"
$MdLines += ""
$MdLines += "Wiadomosci znalezionych: $($AllMessages.Count)"
$MdLines += ""
$MdLines += "---"
$MdLines += ""
$MdLines += "## Watki z Najwieksza Liczba Trafien"
$MdLines += ""
$MdLines += "| Watek | Liczba wiadomosci |"
$MdLines += "|:------|------------------:|"

$ThreadsWithHits.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 15 | ForEach-Object {
    $MdLines += "| $($_.Key) | $($_.Value) |"
}

$MdLines += ""
$MdLines += "---"
$MdLines += ""
$MdLines += "## Wiadomosci Per Dzien"

foreach ($Date in ($DailyMessages.Keys | Sort-Object)) {
    $Msgs = $DailyMessages[$Date]
    $MdLines += ""
    $MdLines += "### $Date ($($Msgs.Count) wiadomosci)"
    $MdLines += ""
    $MdLines += "| Godz | Nadawca | Tresc | Watek | Slowa kluczowe |"
    $MdLines += "|:-----|:--------|:------|:------|:---------------|"
    
    $Counter = 0
    foreach ($Msg in $Msgs) {
        if ($Counter -ge 30) {
            $MdLines += ""
            $MdLines += "...i $($Msgs.Count - 30) wiecej wiadomosci tego dnia"
            break
        }
        $ContentLen = [Math]::Min(100, $Msg.content.Length)
        $ContentShort = $Msg.content.Substring(0, $ContentLen) -replace "`n", " " -replace "\|", "-"
        if ($Msg.content.Length -gt 100) { $ContentShort += "..." }
        $MdLines += "| $($Msg.time) | $($Msg.sender) | $ContentShort | $($Msg.thread) | $($Msg.keywords) |"
        $Counter++
    }
}

$MdLines -join "`n" | Out-File -FilePath $OutputMd -Encoding UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ZAKONCZONO!" -ForegroundColor Green
Write-Host "Znaleziono $($AllMessages.Count) wiadomosci w $($ThreadsWithHits.Count) watkach"
Write-Host "JSON: $OutputJson"
Write-Host "Markdown: $OutputMd"
