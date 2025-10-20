param(
    [string]$BaseUrl = 'https://sanand0.github.io/tdsdata/crawl_html/',
    [string]$Dest = 'week 5\\crawl_with_cli',
    [int]$MaxDepth = 200
)

if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest | Out-Null }

$visited = @{}
$queue = New-Object System.Collections.Generic.Queue[PSObject]
$queue.Enqueue([pscustomobject]@{ url = $BaseUrl; depth = 0 })

function Normalize-Url($href, $contextUrl) {
    if (-not $href) { return $null }
    $href = $href.Trim()
    # ignore javascript:, mailto: etc
    if ($href -match '^(javascript:|mailto:|#)') { return $null }

    if ($href -match '^https?://') { return $href }

    # absolute path starting with /
    if ($href.StartsWith('/')) {
        # get scheme+host from BaseUrl
        $u = [System.Uri] $BaseUrl
        return $u.Scheme + '://' + $u.Host + $href
    }

    # relative to contextUrl
    try {
        $baseUri = [System.Uri] $contextUrl
        $newUri = New-Object System.Uri($baseUri, $href)
        return $newUri.AbsoluteUri
    } catch {
        return $null
    }
}

while ($queue.Count -gt 0) {
    $item = $queue.Dequeue()
    $url = $item.url
    $depth = $item.depth

    if ($visited.ContainsKey($url)) { continue }
    $visited[$url] = $true

    try {
        $r = Invoke-WebRequest $url -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Output "FAILED FETCH: $url"
        continue
    }

    # Only save HTML responses
    $contentType = $r.Headers['Content-Type'] -as [string]
    if ($contentType -and $contentType -notmatch 'html') {
        # skip non-html
    } else {
        # derive filename
        $fileName = [IO.Path]::GetFileName([System.Uri]::UnescapeDataString((New-Object System.Uri($url)).AbsolutePath))
        if (-not $fileName) { $fileName = 'index.html' }
        $out = Join-Path $Dest $fileName
        try {
            $r.Content | Out-File -Encoding utf8 -FilePath $out
            Write-Output "SAVED $out"
        } catch {
            Write-Output "FAILED SAVE $out"
        }
    }

    if ($depth -ge $MaxDepth) { continue }

    # extract links and enqueue
    # extract links (Invoke-WebRequest parses anchors into .Links)
    $hrefs = @()
    if ($r.Links) {
        $hrefs = $r.Links | ForEach-Object { $_.href } | Where-Object { $_ }
    }

    foreach ($h in $hrefs) {
        $abs = Normalize-Url $h $url
        if (-not $abs) { continue }
        # only follow links within the same base path
        if ($abs.StartsWith($BaseUrl) -or $abs -match '^https?://sanand0.github.io/tdsdata/crawl_html') {
            # optionally only follow .html
            if ($abs -match '\.html?$') {
                if (-not $visited.ContainsKey($abs)) {
                    $queue.Enqueue([pscustomobject]@{ url = $abs; depth = $depth + 1 })
                }
            }
        }
    }
}

# write out list and NY count
$files = Get-ChildItem -Path $Dest -File -Filter '*.html' | ForEach-Object { $_.Name } | Sort-Object -Unique
$files | Out-File -FilePath (Join-Path $Dest 'all_html_list.txt') -Encoding utf8
$ny = $files | Where-Object { $_ -match '^[N-Yn-y].*\.html$' }
Write-Output "TOTAL_DOWNLOADED=$($files.Count)"
Write-Output "NY_COUNT=$($ny.Count)"
Write-Output "WROTE LIST: " + (Join-Path $Dest 'all_html_list.txt')
