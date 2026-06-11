# hermes-agent

愛馬仕龍蝦 HermesAgent 知識庫 + Claude 串接 TouchDesigner / Unity / Blender 的 3D 自動化 skill。

## 內容

- `SKILL.md`：HermesAgent 安裝設定知識庫
- `.claude/skills/3d-pipeline/`：TD / Unity / Blender 串接總調度
- `.claude/skills/blender/`：Blender 自動建模（無頭模式，輸出 .blend + 預覽圖）
- `.claude/skills/unity/`：Unity 批次模式建專案、搭場景、掛機制腳本
- `.claude/skills/touchdesigner/`：TD HTTP 橋接，即時建節點網路、存 .toe
- `tools/detect-apps.ps1`：偵測本機三套軟體的安裝路徑

## 在自己電腦上使用（Windows PowerShell）

這些 skill 必須在**本機**的 Claude Code 執行，才能操作你電腦上的 Blender / Unity / TD：

```powershell
# 1. 取得 repo（已 clone 過則 git pull）
git clone https://github.com/chuanontree/hermes-agent.git
cd hermes-agent

# 2. 在 repo 目錄啟動 Claude Code（未安裝先執行 irm https://claude.ai/install.ps1 | iex）
claude
```

啟動後直接用中文下指令，例如：

- 「串接 Blender，幫我建一個有城堡和護城河的場景」
- 「串接 Unity，建一個第三人稱角色可以走動的測試關卡」
- 「串接 TD，做一個音訊反應的噪聲視覺」

產出的專案統一放在 `projects/<工具>/<專案名>/`，都是可以直接打開的格式
（`.blend` / Unity 專案資料夾 / `.toe`）。

### TouchDesigner 首次設定

TD 沒有無頭模式，第一次需手動建立橋接：開 TD → Alt+T 開 Textport →
貼上 `.claude/skills/touchdesigner/scripts/bootstrap_bridge.py` 全文執行 →
File > Save 存成 `.claude/skills/touchdesigner/scripts/claude_bridge.toe`。
之後 Claude 會自動用這個檔啟動 TD 並透過 port 9981 下指令。
