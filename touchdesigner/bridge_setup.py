"""
Hermes TD Bridge Setup
======================
在 TouchDesigner 的 Textport 中執行這段程式碼（F5 開啟 Textport）。
只需要執行一次。之後每次 Hermes 生成新專案時，TD 會自動執行。

使用方式：
  1. 開啟 TouchDesigner
  2. 按 F5 開啟 Textport
  3. 複製整個檔案的內容
  4. 貼上後按 Enter
  5. 看到 "Hermes TD Bridge ready!" 即成功

注意：這段程式碼使用 TouchDesigner 內部的 Python 環境，
      不能在外部 Python 環境中直接執行。
"""

import os
from pathlib import Path

LIVE_FILE = str(Path.home() / ".hermes" / "td_live.py")

# Ensure the live code file exists
Path(LIVE_FILE).parent.mkdir(parents=True, exist_ok=True)
if not Path(LIVE_FILE).exists():
    Path(LIVE_FILE).write_text(
        "# Hermes TD Live Code — waiting for first project...\nprint('Hermes ready!')\n",
        encoding="utf-8",
    )

comp = op("/project1")

# ── Clean up any previous bridge nodes ────────────────────────────────────────
for existing in comp.ops("hermes_bridge_*"):
    existing.destroy()

# ── Text DAT: watches the live file and holds its content ─────────────────────
watcher = comp.create(textDAT, "hermes_bridge_watcher")
watcher.par.file = LIVE_FILE
watcher.par.syncfile = True          # sync to file on disk
watcher.par.loadonstartup = True     # reload when TD opens
watcher.nodeX = -200
watcher.nodeY = -300
watcher.comment = "Hermes: watches ~/.hermes/td_live.py"
watcher.showDATViewer = False

# ── Execute DAT: runs when the file changes ───────────────────────────────────
runner = comp.create(executeDAT, "hermes_bridge_runner")
runner.par.dat = watcher.path
runner.par.tablechange = True        # trigger on content change
runner.nodeX = 100
runner.nodeY = -300
runner.comment = "Hermes: auto-executes new TD code"

runner.text = '''# Hermes TD Bridge — auto-executes code from ~/.hermes/td_live.py
# Do not edit this DAT manually.

def onTableChange(dat):
    """Runs whenever Hermes writes a new project to the live file."""
    code = dat.text
    if not code or code.strip().startswith("# Hermes TD Live Code — waiting"):
        return
    try:
        exec(
            compile(code, "<hermes_live>", "exec"),
            {"comp": op("/project1"), "op": op, "me": me, "print": print},
        )
        print(f"[Hermes] ✅ Project loaded from {dat.par.file.eval()}")
    except Exception as e:
        print(f"[Hermes] ❌ Error in generated code: {e}")
'''

print(f"✅ Hermes TD Bridge ready!")
print(f"📡 Watching: {LIVE_FILE}")
print(f"   Now send a message to your Telegram bot describing the TD project you want!")
