# 偵測本機已安裝的 Blender / Unity / TouchDesigner，輸出 JSON
$ErrorActionPreference = 'SilentlyContinue'

function Find-First($patterns) {
    foreach ($p in $patterns) {
        $hit = Get-ChildItem -Path $p -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending | Select-Object -First 1
        if ($hit) { return $hit.FullName }
    }
    return $null
}

$blender = Find-First @(
    "C:\Program Files\Blender Foundation\Blender*\blender.exe",
    "$env:LOCALAPPDATA\Programs\Blender Foundation\Blender*\blender.exe"
)
if (-not $blender) { $blender = (Get-Command blender -ErrorAction SilentlyContinue).Source }

$unity = Find-First @(
    "C:\Program Files\Unity\Hub\Editor\*\Editor\Unity.exe",
    "C:\Program Files\Unity*\Editor\Unity.exe"
)

$td = Find-First @(
    "C:\Program Files\Derivative\TouchDesigner*\bin\TouchDesigner.exe"
)

[PSCustomObject]@{
    blender       = $blender
    unity         = $unity
    touchdesigner = $td
} | ConvertTo-Json
