---
name: touchdesigner-creator
version: 1.0.0
description: >
  TouchDesigner 自動專案生成技能。
  當使用者透過 Telegram 描述想要的 TouchDesigner 互動裝置、
  聲音視覺作品、生成藝術或任何視覺影像專案時，
  自動在使用者本機電腦上的 TouchDesigner 中建立並執行該專案。
  支援音響反應視覺、生成藝術、互動裝置、3D 幾何、粒子系統等各種類型。

tags: [touchdesigner, TD, 視覺藝術, 互動裝置, 聲音視覺, generative, creative-coding, 生成藝術]
---

# TouchDesigner 自動專案生成技能

## 功能說明

使用者透過 Telegram 描述他們想要的 TouchDesigner 作品，HermesAgent 會：
1. 理解創意描述（繁體中文或英文皆可）
2. 呼叫 `create_td_project` MCP 工具
3. 工具使用 Claude AI 生成對應的 TouchDesigner Python 程式碼
4. 將程式碼寫入 `~/.hermes/td_live.py`
5. 本機 TouchDesigner 中的橋接 DAT 偵測到檔案變化，自動執行程式碼
6. 使用者螢幕上的 TouchDesigner 即時呈現新專案

## 使用 MCP 工具的時機

當使用者說以下類型的話時，呼叫 `create_td_project`：
- 「我要一個...的 TouchDesigner 作品」
- 「幫我做一個視覺效果...」
- 「建立一個 TD 專案...」
- 「我想要音響反應的...」
- 「做一個生成藝術...」
- 任何提到 TouchDesigner、TD、視覺藝術、互動裝置的需求

## 可生成的專案類型

### 音響反應視覺（Audio Reactive）
關鍵詞：音響、音樂、聲音、節拍、beat、audio
範例：「音量越大顏色越亮的頻譜視覺化」、「隨音樂節拍跳動的幾何圖形」

### 生成藝術（Generative Art）
關鍵詞：生成、程序、隨機、緩慢變化
範例：「流動的有機曲線，帶有夢幻色彩」、「無限變化的抽象圖案」

### 互動裝置（Interactive）
關鍵詞：互動、滑鼠、鍵盤、觸控、手勢
範例：「滑鼠控制粒子流向的互動裝置」

### 3D 幾何（3D Geometry）
關鍵詞：3D、立體、球體、幾何、旋轉、mesh
範例：「緩慢旋轉的 3D 球體，帶有 noise 扭曲」

### 粒子系統（Particles）
關鍵詞：粒子、煙霧、流體、particle
範例：「漂浮的粒子群，隨音樂律動」

### Feedback 殘影
關鍵詞：殘影、feedback、trail、拖尾
範例：「帶有殘影效果的動態圖形，越來越暗」

## MCP 工具參數說明

### create_td_project（主要工具）
- `description`（必填）：作品的完整描述，越詳細越好
  - 說明視覺效果、色彩、動態方式、互動元素
  - 例："藍色和紫色的漸層背景，有音響反應的 noise 紋理，音量大時整個畫面變亮，有輕微的 feedback 殘影"
- `project_name`（選填）：英文專案名稱，預設 "hermes_project"
- `launch`（選填）：是否自動啟動 TD，預設 true

### list_td_projects
列出已生成的所有 TD 專案（最新排最前）

### launch_touchdesigner
手動啟動 TouchDesigner

### get_latest_td_code
取得最新生成的程式碼（方便手動貼進 TD）

## 回覆使用者的方式

成功生成後，告訴使用者：
- 正在建立什麼類型的作品
- 程式碼已傳送到 TouchDesigner
- 如果 TD 未開啟，提示需要先設定 bridge 或開啟 TD
- 如果他想調整，可以繼續描述（例如「把顏色改成紅色」）

## 安裝與設定（一次性設定）

### 第一步：安裝套件
```bash
pip install -r hermes-agent/touchdesigner/requirements.txt
```

### 第二步：在 HermesAgent 設定 MCP Server

在 `~/.hermes/mcp.json` 中加入（若無此檔則新建）：

```json
{
  "mcpServers": {
    "touchdesigner": {
      "command": "python",
      "args": ["/完整路徑/hermes-agent/touchdesigner/td_mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "你的_Anthropic_API_Key",
        "TD_PATH": "/Applications/TouchDesigner.app/Contents/MacOS/TouchDesigner"
      }
    }
  }
}
```

> `TD_PATH` 為選填；省略則自動搜尋標準安裝路徑。

重啟 HermesAgent Gateway 使設定生效。

### 第三步：設定 TouchDesigner Bridge（只需做一次）

1. 開啟 TouchDesigner
2. 按 `F5` 開啟 Textport
3. 複製 `touchdesigner/bridge_setup.py` 的全部內容，貼上並按 Enter
4. 看到 "Hermes TD Bridge ready!" 表示成功

儲存這個 `.toe` 檔案（例如 `hermes_bridge.toe`），之後直接開啟它即可。

## 整體運作流程

```
Telegram 訊息：「我要一個音響反應的藍色粒子視覺」
        ↓
HermesAgent 辨識為 TD 專案需求
        ↓
呼叫 MCP: create_td_project(description="音響反應的藍色粒子視覺")
        ↓
td_generator.py 使用 Claude API 生成 TouchDesigner Python 程式碼
        ↓
寫入 ~/.hermes/td_live.py
        ↓
TouchDesigner 中的 hermes_bridge_watcher (textDAT) 偵測到檔案更新
        ↓
hermes_bridge_runner (executeDAT) 自動執行新程式碼
        ↓
TouchDesigner 即時呈現新的視覺作品
        ↓
Telegram 回覆：「✅ 已建立音響反應粒子視覺！請查看 TouchDesigner。」
```

## 使用者對話範例

**使用者**：我要一個音響反應的視覺，藍色和紫色漸層，隨音量起伏

**AI 應回應**：呼叫 `create_td_project`，description 填入完整描述，然後告知使用者已生成。

**使用者**：加上 feedback 殘影效果

**AI 應回應**：再次呼叫 `create_td_project`，在描述中加入前次的需求 + 新的殘影要求，重新生成完整專案。

**使用者**：換成紅色和橘色

**AI 應回應**：同樣重新呼叫工具，描述更新為最新要求。

## TouchDesigner 常用路徑

| 平台 | 預設路徑 |
|------|---------|
| Mac | `/Applications/TouchDesigner.app/Contents/MacOS/TouchDesigner` |
| Windows | `C:\Program Files\Derivative\TouchDesigner\bin\TouchDesigner.exe` |
| Linux | `~/derivative/TouchDesigner.*/bin/TouchDesigner` |

## 生成的檔案位置

| 檔案 | 路徑 |
|------|------|
| 即時執行碼 | `~/.hermes/td_live.py` |
| 專案存檔 | `~/.hermes/td_projects/<name>_<timestamp>.py` |
| 元資料 | `~/.hermes/td_projects/<name>_<timestamp>.json` |
