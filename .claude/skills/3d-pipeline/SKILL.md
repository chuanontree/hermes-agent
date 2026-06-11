---
name: 3d-pipeline
description: >
  TD / Unity / Blender 串接總調度。當使用者說「串接 Blender」「串接 Unity」「串接 TD」
  或提出建模、搭場景、做機制、做視覺等 3D 相關需求但未指明工具時，先用本 skill
  判斷該交給哪一套，再轉交對應的 blender / unity / touchdesigner skill 執行。
---

# 3D Pipeline 總調度

使用者可隨時指名要串接哪一套軟體；指名了就直接用對應 skill，不用再問。

## 分流原則（使用者未指名時）

| 需求類型 | 交給 |
|---------|------|
| 建模、雕刻、材質、寫實渲染、物理模擬、3D 動畫資產 | **blender** skill |
| 遊戲場景、互動機制、可操作角色、關卡、要進引擎的東西 | **unity** skill |
| 即時視覺、VJ、互動裝置、音訊反應、投影、節點網路 | **touchdesigner** skill |
| 跨軟體（如 Blender 建模 → Unity 用） | blender 先產出，匯出 FBX（`bpy.ops.export_scene.fbx`）放進 Unity 專案 Assets |

## 共同約定

- 第一次使用先跑 `powershell -File tools/detect-apps.ps1` 找到三套軟體的 exe 路徑並記住。
- 所有產出的專案統一放在 repo 的 `projects/<工具>/<專案名>/`，且**必須是使用者
  雙擊或用官方工具就能打開的格式**（.blend / Unity 專案資料夾 / .toe）。
- 完成後回報：專案路徑 + 怎麼打開 + 建了什麼。
- 後續修改同一專案：沿用同一資料夾迭代，不要另開新專案。
