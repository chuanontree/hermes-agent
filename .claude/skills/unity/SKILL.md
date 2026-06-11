---
name: unity
description: >
  用 Unity 批次模式（-batchmode）自動建立專案、搭建場景、放置物件、掛上 C# 機制腳本，
  產出使用者可用 Unity Hub / Unity Editor 直接打開的完整專案。
  當使用者要求「用 Unity 建場景 / 做遊戲機制 / 建專案」時使用本 skill。
  全程透過 PowerShell 操作 Unity.exe。
---

# Unity 自動化 Skill

## 運作模式

1. **找到 Unity.exe**（記住路徑，之後重用）：
   ```powershell
   powershell -File tools/detect-apps.ps1
   ```
   Unity 通常在 `C:\Program Files\Unity\Hub\Editor\<版本>\Editor\Unity.exe`。

2. **建立新專案**（已存在則跳過）：
   ```powershell
   & $UNITY -batchmode -quit -createProject "projects/unity/<專案名>" -logFile "projects/unity/<專案名>/create.log"
   ```

3. **放入橋接腳本**：把本 skill 的 `Editor/ClaudeBridge.cs` 複製到
   `projects/unity/<專案名>/Assets/Editor/ClaudeBridge.cs`。

4. **依使用者需求產生場景描述 JSON**，寫到 `projects/unity/<專案名>/claude_scene.json`
   （格式見下方）。需要遊戲機制（移動、旋轉、觸發等）時，把 C# MonoBehaviour 腳本直接寫進
   `Assets/Scripts/`，並在 JSON 的物件上用 `"components"` 掛上。

5. **批次執行建場景**：
   ```powershell
   & $UNITY -batchmode -quit -projectPath "projects/unity/<專案名>" -executeMethod ClaudeBridge.BuildScene -logFile "projects/unity/<專案名>/build.log"
   ```

6. **驗證**：用 Read/Grep 檢查 `build.log` 有 `[ClaudeBridge] DONE`、沒有 C# 編譯錯誤
   （搜 `error CS`）。失敗就修腳本重跑。

7. 告訴使用者：用 Unity Hub「Add project」選 `projects/unity/<專案名>` 即可打開，
   場景在 `Assets/Scenes/Main.unity`。

## claude_scene.json 格式

```json
{
  "sceneName": "Main",
  "objects": [
    { "name": "Ground",  "primitive": "Plane",  "position": [0, 0, 0],   "scale": [4, 1, 4],
      "color": [0.3, 0.5, 0.3] },
    { "name": "Player",  "primitive": "Capsule","position": [0, 1, 0],
      "components": ["PlayerMove"], "rigidbody": true },
    { "name": "Spinner", "primitive": "Cube",   "position": [3, 0.5, 0], "rotation": [0, 45, 0],
      "color": [0.9, 0.4, 0.1], "components": ["Rotator"] },
    { "name": "Sun",     "light": "Directional", "rotation": [50, -30, 0], "intensity": 1.2 },
    { "name": "MainCamera", "camera": true, "position": [0, 6, -10], "lookAt": [0, 0, 0] }
  ]
}
```

支援欄位：`primitive`（Cube/Sphere/Capsule/Cylinder/Plane/Quad）、`empty: true`、
`light`（Directional/Point/Spot）+ `intensity`、`camera: true` + `lookAt`、
`position/rotation/scale`、`color`、`rigidbody`（bool 或 `{"mass":2,"kinematic":false}`）、
`components`（要 AddComponent 的腳本類別名稱，需先寫好對應 .cs）、`parent`（父物件名）。

## 規則

- 機制邏輯一律寫成正規 MonoBehaviour 放 `Assets/Scripts/`，不要塞進 ClaudeBridge。
- 每次重跑 BuildScene 會整個重建 Main 場景（冪等），後續修改改 JSON / .cs 再重跑即可。
- Unity 批次模式一次只能一個實例開同一專案；若 log 出現專案被鎖住，請使用者先關掉
  Editor 中開著的該專案。
- 第一次建專案 + 編譯需要數分鐘，PowerShell 指令 timeout 設長一點（600000ms）。
