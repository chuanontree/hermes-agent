---
name: touchdesigner
description: >
  串接 TouchDesigner：透過 HTTP 橋接（WebServer DAT）即時在 TD 內建立節點網路、
  設定參數、搭建視覺機制，並存成使用者可打開的 .toe 專案。
  當使用者要求「串接 TD / 用 TouchDesigner 做視覺 / 建 TD 網路」時使用本 skill。
  透過 PowerShell 啟動 TD 並用 scripts/td-send.ps1 傳送 Python 指令。
---

# TouchDesigner 串接 Skill

TD 的 .toe 是二進位檔且沒有無頭模式，所以採用**即時橋接**：
TD 開著，內部跑一個 WebServer DAT（port 9981），Claude 用 PowerShell POST Python
程式碼進去執行，最後叫 TD 自己存檔成 .toe。

## 首次啟動橋接（每台機器只需設定一次）

1. 找到 TD：`powershell -File tools/detect-apps.ps1`
   （通常在 `C:\Program Files\Derivative\TouchDesigner\bin\TouchDesigner.exe`）
2. 啟動 TD 並自動載入橋接（TD 啟動時會執行同目錄的 bootstrap）：
   ```powershell
   & $TD ".claude/skills/touchdesigner/scripts/claude_bridge.toe"
   ```
   若還沒有 claude_bridge.toe（第一次）：請使用者打開 TD，按 Alt+T 開 Textport，
   貼上並執行 `scripts/bootstrap_bridge.py` 全文，橋接即建立，
   並請使用者 File > Save 存成 `scripts/claude_bridge.toe` 供之後自動啟動。
3. 驗證橋接活著：
   ```powershell
   powershell -File .claude/skills/touchdesigner/scripts/td-send.ps1 -Code "result = app.version"
   ```

## 對 TD 下指令

把要在 TD 內執行的 Python 寫進暫存檔，再送過去（程式碼在 TD 的全域環境執行，
可用 op()/parent()/project 等完整 TD API；把要回傳的值指定給變數 `result`）：

```powershell
powershell -File .claude/skills/touchdesigner/scripts/td-send.ps1 -File "projects/td/<專案名>/build_step.py"
```

建造網路範例（build_step.py）：

```python
base = op('/project1')
noise = base.create(noiseTOP, 'noise1')
noise.par.resolutionw, noise.par.resolutionh = 1280, 720
blur = base.create(blurTOP, 'blur1')
blur.par.size = 12
blur.inputConnectors[0].connect(noise)
out = base.create(outTOP, 'out1')
out.inputConnectors[0].connect(blur)
result = 'network built'
```

## 存成使用者可開啟的專案

```powershell
powershell -File .claude/skills/touchdesigner/scripts/td-send.ps1 -Code "project.save('projects/td/<專案名>/<專案名>.toe'); result='saved'"
```
（路徑用絕對路徑最保險。）存好後使用者雙擊 .toe 即可開啟。

## 規則

- 每一步都檢查 td-send 的回傳 JSON：`ok=true` 才繼續，`error` 內容用來修正程式碼。
- 建新專案時先在 `/project1` 下清出或建立一個專用 Base COMP（如 `/project1/claude_<專案名>`），
  避免覆蓋使用者既有網路。
- 常用節點族：`noiseTOP, movieFileInTOP, blurTOP, levelTOP, compositeTOP, renderTOP,
  geometryCOMP, cameraCOMP, lightCOMP, sphereSOP, boxSOP, noiseSOP, lfoCHOP, noiseCHOP,
  mathCHOP, audioFileInCHOP, audioSpectrumCHOP, constantMAT, phongMAT`。
  CHOP 控參數用 export 或 expression：`op('blur1').par.size.expr = "op('lfo1')['chan1']*20"`。
- 橋接沒回應時：確認 TD 有開、橋接 toe 有載入；必要時請使用者重貼 bootstrap_bridge.py。
