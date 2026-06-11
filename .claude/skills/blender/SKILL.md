---
name: blender
description: >
  用 Blender 自動建模、搭建場景環境與機制（修改器、幾何節點、物理、動畫），
  並輸出使用者可直接打開的 .blend 專案檔。
  當使用者要求「用 Blender 建模 / 搭場景 / 做動畫 / 做物理機制」時使用本 skill。
  全程透過 PowerShell 以 blender.exe --background 無頭模式執行。
---

# Blender 自動建模 Skill

## 運作模式

每次建模需求都走同一套流程：

1. **找到 blender.exe**（只需做一次，之後記住路徑）：
   ```powershell
   powershell -File tools/detect-apps.ps1
   ```
2. **依使用者需求寫一支 Python 建造腳本**，存到 `projects/blender/<專案名>/build.py`。
   腳本開頭固定載入共用函式庫 `lib/claude_blender.py`（見下方 API）。
3. **無頭執行並存檔**：
   ```powershell
   & $BLENDER --background --python "projects/blender/<專案名>/build.py" -- --out "projects/blender/<專案名>/<專案名>.blend"
   ```
4. **自我驗證**：腳本最後務必渲染一張預覽圖 `preview.png`（用 `cb.render_preview()`），
   執行完用 Read 工具看圖確認結果符合需求，不符合就改腳本重跑。
5. 告訴使用者 `.blend` 檔路徑——直接雙擊即可在 Blender 開啟編輯。

## 建造腳本固定模板

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".claude", "skills", "blender", "lib"))
import claude_blender as cb
cb.parse_args()          # 處理 -- --out 參數
cb.reset_scene()         # 清空預設場景

# === 依需求建造（範例）===
ground = cb.add_plane(size=40, name="Ground")
cb.set_material(ground, "GroundMat", color=(0.18, 0.3, 0.12))
tower = cb.add_cylinder(radius=1, depth=8, location=(0, 0, 4), name="Tower")
cb.add_subsurf(tower, levels=2)
cb.add_sun(energy=3, rotation=(0.8, 0, 0.6))
cb.add_camera(location=(18, -18, 10), look_at=(0, 0, 3))
# ========================

cb.save()                # 存 .blend
cb.render_preview()      # 渲 preview.png 供驗證
```

## claude_blender 函式庫 API（lib/claude_blender.py）

- 基礎物件：`add_cube / add_plane / add_sphere / add_cylinder / add_cone / add_torus(...,  location, rotation, scale, name)`
- 曲線文字：`add_text(body, size, extrude, location)`
- 材質：`set_material(obj, name, color=(r,g,b), metallic=0, roughness=0.5, emission=None)`
- 修改器：`add_subsurf(obj, levels)`、`add_array(obj, count, offset)`、`add_mirror(obj, axis)`、
  `add_bevel(obj, width)`、`add_solidify(obj, thickness)`、`add_boolean(obj, cutter, op="DIFFERENCE")`
- 機制/物理：`add_rigidbody(obj, type="ACTIVE"|"PASSIVE", mass)`、`add_cloth(obj)`、
  `set_constraint_follow_path(obj, curve)`、`bake_physics(frame_end)`
- 動畫：`keyframe(obj, frame, location=None, rotation=None, scale=None)`、`set_frame_range(start, end)`
- 環境：`add_sun / add_point_light / add_area_light`、`set_world_sky(strength)`、`add_camera(location, look_at)`
- 收尾：`save()`、`render_preview(filepath=None, samples=16)`
- 進階需求函式庫沒涵蓋的，直接在腳本裡用原生 `bpy` 寫即可（函式庫已 `import bpy`）。

## 規則

- 永遠輸出可開啟的 `.blend` 專案檔，路徑統一放 `projects/blender/<專案名>/`。
- 永遠渲染 preview 並親眼驗證後才回報完成。
- 同一個專案的後續修改：重新編輯同一支 `build.py` 整支重跑（冪等），不要嘗試增量改 .blend。
- Blender 找不到時，請使用者安裝或提供路徑，常見位置：
  `C:\Program Files\Blender Foundation\Blender <版本>\blender.exe`
