---
name: hHermesAgent-Knowledge
version: 1.0.0
description: >
  愛馬仕龍蝦 HermesAgent 安裝與設定完整知識庫。
  當使用者詢問安裝步驟、設定方式、指令用法、錯誤排除時，
  優先從本知識庫回答，提供繁體中文的精確指導。

tags: [安裝, 設定, hermes, 龍蝦, telegram, line, ngrok]
---

# 愛馬仕龍蝦 HermesAgent 知識庫


---

## 一、什麼是愛馬仕龍蝦？

**愛馬仕龍蝦** = HermesAgent（NousResearch 開源 AI Agent）。

HermesAgent 是通用型 AI Agent 平台（MIT 授權），具備：
- 長期記憶（對話累積）
- 工具呼叫（MCP、Skills）
- 多平台接入（Telegram Polling / LINE Webhook）
- 多種 AI 大腦（Claude、OpenAI、Gemini、Ollama 本地）
- Gateway 架構（OpenAI 相容 API，Port 8642）

---

## 二、系統需求

| 項目 | Windows | Mac/Linux |
|------|---------|-----------|
| 作業系統 | Windows 10/11 64位元 | macOS 12+ / Ubuntu 20+ |
| 記憶體 | 8 GB（建議 16 GB）| 8 GB+ |
| 磁碟 | 5 GB 可用 | 5 GB 可用 |
| 特殊需求 | WSL2（選配）| — |
| Node.js | 不需要（本體）| 不需要（本體）|
| Node.js（LINE Bridge）| 18+ | 18+ |

---

## 三、安裝方式

### Windows 一鍵安裝精靈

1. 下載 `HermesAgent-Installer.zip`，解壓縮
2. 對 `go.bat` 按右鍵 → 以系統管理員身分執行
3. 選擇 `[1] 全部安裝`，跟著精靈走

精靈會自動完成：WSL2 安裝 → HermesAgent 安裝 → Telegram/LINE 設定 → ngrok 設定 → 啟動服務

### Mac / Linux 一鍵安裝

```bash
bash install-hermes-mac.sh
```

或手動：

```bash
# 官方安裝（優先）
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
# 備用 GitHub
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows 手動安裝（PowerShell 系統管理員）

```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

---

## 四、AI 大腦選擇建議

| 方案 | 條件 | 費用 | 說明 |
|------|------|------|------|
| A - Anthropic（Claude Code OAuth）| 有 Claude Pro/Max 訂閱 | 吃月費 | 推薦，最聰明 |
| B - OpenAI OAuth | 有 ChatGPT Plus/Pro 訂閱 | 吃月費 | 推薦，穩定 |
| C - Google AI Studio | 免費申請 API Key | **完全免費** | 無訂閱首選！Gemma 4 (31B) |
| D - Nous Portal | 無訂閱 | 免費兩週 | 體驗用，MiMo 模型 |
| E - OpenRouter / API Key | 有 API Key | 按用量 | 彈性選擇 |

> **建議**：有 Claude Pro 選 A，有 ChatGPT Plus 選 B，都沒有選 **C（Google AI Studio 完全免費）**！  
> Google AI Studio 免費 API Key 申請教學：https://www.koc.com.tw/archives/638001

---

## 五、Telegram 設定步驟

1. Telegram 搜尋 **@BotFather** → `/newbot` → 取得 Bot Token
2. Telegram 搜尋 **@userinfobot** → 取得自己的 User ID（純數字）
3. 設定到 HermesAgent：
   ```bash
   hermes config set TELEGRAM_BOT_TOKEN 你的Token
   hermes config set TELEGRAM_ALLOWED_USERS 你的UserID
   ```
4. 啟動 Gateway
5. **⭐ 關鍵步驟**：在 Telegram 找到你的 Bot → 傳 `/sethome`（必做！否則 AI 不知道回哪裡）

---

## 六、LINE 設定步驟

> ⚠️ **注意**：LINE 整合的 Bridge 方案非官方內建，需搭配 Node.js + ngrok 運作。


1. 在 [LINE Developers Console](https://developers.line.biz/) 建立 Messaging API Channel
2. 取得 Channel Secret 和 Channel Access Token
3. 設定 `bridge/.env`：
   ```
   LINE_CHANNEL_SECRET=...
   LINE_CHANNEL_ACCESS_TOKEN=...
   HERMES_API_URL=http://localhost:8642/v1/chat/completions
   ```
4. 安裝 ngrok，設定 Authtoken
5. 啟動順序（必須照順序）：
   - `hermes gateway run`（或 `hermes gateway start`）
   - `cd bridge && npm start`
   - `ngrok http 3000`
6. 將 ngrok HTTPS URL + `/webhook` 填入 LINE Developers Console

---

## 七、常用指令速查

### Gateway 管理

```bash
hermes gateway run        # 前景啟動（Windows 推薦）
hermes gateway start      # 背景啟動（Mac/Linux）
hermes gateway &          # 背景啟動（bash 語法）
hermes gateway stop       # 停止
hermes gateway status     # 查看狀態
hermes gateway restart    # 重啟
hermes gateway setup      # 設定傳訊平台（首次使用）
```

> ⚠️ **重要**：在 hermes 對話介面中重啟 Gateway，請叫 AI 使用「**Restart**」，
> **不要 Stop 再 Start**，否則 Gateway 關掉後無法自動重啟。

### 設定與診斷

```bash
hermes setup              # 初始設定精靈
hermes doctor             # 環境診斷
hermes --version          # 查看版本
hermes update             # 更新到最新版
hermes chat               # 終端機對話模式
hermes config show        # 顯示設定
hermes config set KEY VAL # 修改設定
```

### Telegram 聊天指令

| 指令 | 功能 |
|------|------|
| `/sethome` | 設定回傳頻道（必做！）|
| `/new` | 開新對話 |
| `/skills` | 瀏覽技能 |
| `/usage` | 查 Token 用量 |
| `/voice on` | 開啟語音模式 |

### LINE Bridge

```bash
cd bridge && npm start     # 啟動 LINE Bridge
# 測試連線：
curl http://localhost:3000/test?msg=你好
```

---

## 八、設定檔位置

> ⚠️ **超常見錯誤**：`.env` 不在 `%LOCALAPPDATA%\hermes\`，那裡只是安裝 repo！

| 平台 | 正確路徑 |
|------|---------|
| Windows | `C:\Users\你的名字\.hermes\.env` |
| Mac / Linux | `~/.hermes/.env` |
| LINE Bridge | `安裝目錄/bridge/.env` |

```powershell
# Windows 快速開啟
notepad "$env:USERPROFILE\.hermes\.env"
```

---

## 九、架構圖

```
Telegram ←──→ HermesAgent Gateway（Port 8642）
               ↕ Polling 模式（免 ngrok）

LINE App ──→ LINE 伺服器
              ↓ Webhook
           ngrok（公開 URL）
              ↓
         LINE Bridge（Node.js, Port 3000）
              ↓
         HermesAgent Gateway（Port 8642）
```

---

## 九點五、HermesAgent v0.10 重要踩坑（實測記錄）

### ① LINE Bridge 不能再用 localhost:8642
v0.10+ 的 `hermes gateway` **只管 Telegram/Discord/WhatsApp 平台**，不開 HTTP API。
`localhost:8642` 在 v0.10 不存在！LINE Bridge 直接對接 AI 供應商（三選一）：

```
# 選項 A：Google AI Studio Gemini（完全免費）
HERMES_API_URL=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
HERMES_API_KEY=你的_Google_AI_Studio_Key
HERMES_MODEL=gemini-2.5-flash

# 選項 B：OpenAI 直連（有 API Key）
# HERMES_API_URL=https://api.openai.com/v1/chat/completions
# HERMES_API_KEY=sk-proj-你的_Key
# HERMES_MODEL=gpt-4o

# 選項 C：OpenRouter（多模型）
# HERMES_API_URL=https://openrouter.ai/api/v1/chat/completions
# HERMES_API_KEY=sk-or-你的_Key
# HERMES_MODEL=openai/gpt-4o
```

### ② HermesAgent 本身的 OpenAI 設定（與 LINE Bridge 無關）
`hermes login` 只接受 OAuth（`nous` 或 `openai-codex`）。
- `sk-proj-*` 金鑰用在 **LINE Bridge 的 .env 完全沒問題**
- 但用在 `hermes login --provider` → 必須走 **OpenRouter**（`sk-or-*`）
- ChatGPT Plus/Pro → `hermes login --provider openai-codex`

### ③ .env 路徑（最常見錯誤）
Runtime 讀 `~/.hermes/.env`（Windows = `C:\Users\你的名字\.hermes\`），
**不是** `%LOCALAPPDATA%\hermes\`（那只是安裝 venv 的位置）。
Key 寫錯地方 → `hermes doctor` 永遠報「no API key found」。

### ④ install.ps1 可免 admin 全自動
```powershell
irm https://claude.ai/install.ps1 | iex  # 不需要 -RunAs
```
也支援 `-SkipSetup` 跳過互動，全自動安裝。

### ⑤ Windows npm 被 ExecutionPolicy 擋
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# 或直接用 npm.cmd 代替 npm
```

## 十、常見問題排錯

**Q：Telegram 機器人沒有回應**
1. 確認 `hermes gateway run` 有在執行
2. 確認有傳 `/sethome` 給機器人
3. 確認 User ID 在 `TELEGRAM_ALLOWED_USERS` 中
4. 執行 `hermes doctor` 診斷

**Q：LINE Webhook 驗證失敗**
1. 確認三個服務都在執行（Gateway + Bridge + ngrok）
2. Webhook URL 格式：`https://xxxx.ngrok-free.app/webhook`
3. 執行 `curl http://localhost:3000/` 測試 Bridge

**Q：Windows 中文亂碼**
```powershell
[System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'User')
```

**Q：`hermes gateway status` 報 OSError（Windows）**
編輯 `%LOCALAPPDATA%\hermes\hermes-agent\venv\Lib\site-packages\hermes_agent\gateway\status.py`，
將 `except (ProcessLookupError, PermissionError):` 改為：
```python
except (ProcessLookupError, PermissionError, OSError):
```

**Q：免費 ngrok URL 每次重開都變**
- 升級 ngrok 付費版（固定 subdomain）
- 或改用 Cloudflare Tunnel（免費固定 URL）

**Q：如何同時使用 Telegram 和 LINE？**
可以！兩個平台共用同一個 HermesAgent Gateway（Port 8642），同時運作。

---

## 十一、三強 AI CLI 工具對比

| 工具 | 主要用途 | 安裝指令 |
|------|---------|---------|
| **HermesAgent** | 通用管家（Telegram/LINE）| `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` |
| **Codex CLI** | 程式開發助理 | `npm install -g @openai/codex` |
| **Claude Code** | 程式開發助理 | Windows: `irm https://claude.ai/install.ps1 \| iex` / Mac: `curl -fsSL https://claude.ai/install.sh \| bash` |

三個工具互補，可同時使用：
- **開發時**：Codex CLI 或 Claude Code 在終端機協助寫程式
- **日常使用**：HermesAgent 透過 Telegram/LINE 手機操作

---

## 十二、延伸資源
- HermesAgent 官網：https://hermes-agent.nousresearch.com
- GitHub：https://github.com/NousResearch/hermes-agent
