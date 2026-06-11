# 把 Python 程式碼送進 TouchDesigner 橋接執行
# 用法:
#   powershell -File td-send.ps1 -Code "result = app.version"
#   powershell -File td-send.ps1 -File build_step.py
param(
    [string]$Code,
    [string]$File,
    [int]$Port = 9981
)

$ErrorActionPreference = 'Stop'

if ($File) {
    $Code = Get-Content -Raw -Encoding UTF8 $File
}
if (-not $Code) {
    Write-Error "需要 -Code 或 -File 參數"
    exit 1
}

$body = @{ code = $Code } | ConvertTo-Json -Depth 4
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/exec" -Method Post `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType 'application/json' -TimeoutSec 60
    $resp | ConvertTo-Json -Depth 6
    if (-not $resp.ok) { exit 2 }
}
catch {
    Write-Output ('{"ok": false, "error": "橋接無回應，確認 TouchDesigner 已開啟且 claude_bridge 已載入: ' + $_.Exception.Message + '"}')
    exit 3
}
