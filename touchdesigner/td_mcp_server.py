#!/usr/bin/env python3
"""
TouchDesigner MCP Server for HermesAgent (愛馬仕龍蝦).

Provides tools that let the AI create and launch TouchDesigner projects
on the user's local machine via natural-language descriptions.

Run with:  python td_mcp_server.py
HermesAgent connects via stdio MCP protocol.
"""

import os
import platform
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from td_generator import LIVE_CODE_FILE, PROJECTS_DIR, generate_td_project

mcp = FastMCP("TouchDesigner Creator", version="1.0.0")

# ── TouchDesigner executable paths by platform ────────────────────────────────

_TD_PATHS = {
    "Darwin": [
        "/Applications/TouchDesigner.app/Contents/MacOS/TouchDesigner",
        "/Applications/TouchDesigner099.app/Contents/MacOS/TouchDesigner",
    ],
    "Windows": [
        r"C:\Program Files\Derivative\TouchDesigner\bin\TouchDesigner.exe",
        r"C:\Program Files (x86)\Derivative\TouchDesigner\bin\TouchDesigner.exe",
    ],
    "Linux": [
        str(p) for p in Path.home().glob("derivative/TouchDesigner.*/bin/TouchDesigner")
    ],
}


def _find_td() -> str | None:
    # Allow override via environment variable
    env_path = os.environ.get("TD_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    for path in _TD_PATHS.get(platform.system(), []):
        if Path(path).exists():
            return path
    return None


def _td_running() -> bool:
    try:
        import psutil
        return any("TouchDesigner" in (p.info.get("name") or "") for p in psutil.process_iter(["name"]))
    except ImportError:
        return False  # psutil optional


def _launch_td(td_path: str) -> str:
    bridge_toe = Path(__file__).parent / "bridge" / "hermes_bridge.toe"
    args = [td_path, str(bridge_toe)] if bridge_toe.exists() else [td_path]
    try:
        subprocess.Popen(args)
        return "✅ TouchDesigner 已啟動！"
    except Exception as e:
        return f"⚠️ 啟動失敗：{e}"


# ── MCP Tools ─────────────────────────────────────────────────────────────────


@mcp.tool()
def create_td_project(
    description: str,
    project_name: str = "hermes_project",
    launch: bool = True,
) -> str:
    """
    根據自然語言描述，在本機 TouchDesigner 中自動建立互動視覺專案。

    Args:
        description: 想要的 TouchDesigner 作品描述（繁中或英文皆可），例如：
                     "音響反應的藍色粒子流，隨著音量增強而擴散"
                     "緩慢旋轉的 3D 球體，帶有 noise 扭曲和粉紅金色漸層"
                     "有 feedback 殘影效果的生成藝術，黑底白線"
        project_name: 專案名稱（英文，無空格），預設 "hermes_project"
        launch: 是否自動啟動 TouchDesigner，預設 True

    Returns:
        操作結果訊息，包含專案路徑與狀態
    """
    result = generate_td_project(description, project_name)

    if not result["success"]:
        return f"❌ 生成失敗：{result['error']}"

    td_status = ""
    if launch:
        td_path = _find_td()
        if not td_path:
            td_status = (
                "\n⚠️ 找不到 TouchDesigner 安裝。請手動開啟 TD，"
                "並確認已執行過 bridge_setup.py 的設定。"
            )
        elif _td_running():
            td_status = "\n✅ 已更新 TouchDesigner 中的專案程式碼。"
        else:
            td_status = "\n" + _launch_td(td_path)

    return (
        f"✅ TouchDesigner 專案已生成！\n"
        f"🎨 類型：{result['project_type']}\n"
        f"📁 程式碼：{result['code_path']}\n"
        f"📡 即時檔：{LIVE_CODE_FILE}"
        + td_status
        + (
            "\n\n💡 首次使用？請在 TouchDesigner Textport（F5）貼上 bridge_setup.py 的內容並執行一次。"
            if not _td_running()
            else ""
        )
    )


@mcp.tool()
def list_td_projects() -> str:
    """列出所有已由 Hermes 生成的 TouchDesigner 專案（最新的排最前面）。"""
    if not PROJECTS_DIR.exists():
        return "尚未生成任何 TouchDesigner 專案。"

    projects = sorted(PROJECTS_DIR.glob("*.py"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not projects:
        return "尚未生成任何 TouchDesigner 專案。"

    from datetime import datetime

    lines = [f"📁 已生成的 TD 專案（共 {len(projects)} 個）：\n"]
    for p in projects[:20]:  # cap at 20
        dt = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        lines.append(f"  • {p.stem}  ({dt})")
    return "\n".join(lines)


@mcp.tool()
def launch_touchdesigner(project_path: str = "") -> str:
    """
    手動啟動 TouchDesigner 應用程式。

    Args:
        project_path: 可選的 .toe 檔案絕對路徑；若省略則開啟空白專案
    """
    td_path = _find_td()
    if not td_path:
        return (
            "❌ 找不到 TouchDesigner。\n"
            "請安裝 TouchDesigner 或設定 TD_PATH 環境變數指向可執行檔。"
        )
    args = [td_path]
    if project_path and Path(project_path).exists():
        args.append(project_path)
    try:
        subprocess.Popen(args)
        return "✅ TouchDesigner 已啟動！"
    except Exception as e:
        return f"❌ 啟動失敗：{e}"


@mcp.tool()
def get_latest_td_code() -> str:
    """取得最近一次生成的 TouchDesigner 程式碼（方便手動複製進 TD Textport）。"""
    if not LIVE_CODE_FILE.exists():
        return "尚未生成任何程式碼。請先使用 create_td_project。"
    code = LIVE_CODE_FILE.read_text(encoding="utf-8")
    return f"最新程式碼（位於 {LIVE_CODE_FILE}）：\n\n```python\n{code}\n```"


if __name__ == "__main__":
    mcp.run()
