#!/usr/bin/env python3
"""TouchDesigner project code generator using Claude API."""

import json
import os
from datetime import datetime
from pathlib import Path

import anthropic

LIVE_CODE_FILE = Path.home() / ".hermes" / "td_live.py"
PROJECTS_DIR = Path.home() / ".hermes" / "td_projects"

TD_SYSTEM_PROMPT = """You are an expert TouchDesigner Python developer.
Generate Python code that creates a complete, working TouchDesigner network.

CRITICAL RULES:
1. Code executes inside TouchDesigner's Python environment (textport or executeDAT)
2. Variable 'comp' is already set to op('/project1') — use it as the container
3. Always start by deleting previous 'hermes_*' nodes to allow re-running
4. All TD operator type names are available as globals (noiseTOP, audioDevInCHOP, etc.)
5. Connect nodes: nodeB.setInputs([nodeA])
6. Set node layout: node.nodeCenterX = x; node.nodeCenterY = y
7. Return ONLY executable Python — no markdown fences, no explanations

CLEANUP (always include at the top):
for n in comp.ops('hermes_*'):
    n.destroy()

NAMING: prefix every created node with 'hermes_'

OPERATOR QUICK REFERENCE:
TOPs (visuals):
  noiseTOP        — procedural noise (par.type='hermite'/'random'/'sparse', par.w, par.h, par.period, par.monochrome)
  rampTOP         — gradient (par.type='horizontal'/'vertical'/'radial', set color keys via par.color0r/g/b etc.)
  levelTOP        — brightness/contrast/invert (par.brightness, par.contrast, par.gamma, par.invert)
  blurTOP         — blur (par.sizex, par.sizey)
  feedbackTOP     — feedback/trails (par.top = source path)
  compositeTOP    — blend/combine (par.operand='add'/'over'/'multiply'/'screen', max 8 inputs)
  transformTOP    — scale/rotate/translate (par.sx, par.sy, par.rz, par.tx, par.ty)
  displaceTOP     — displacement (par.scalex, par.scaley)
  thresholdTOP    — threshold
  glslTOP         — GLSL shader (par.glsl = shader code string)
  movieFileInTOP  — video/image file (par.file)
  outTOP          — final output (ALWAYS create one)

SOPs (3D geometry):
  boxSOP, sphereSOP (par.rows, par.cols), gridSOP, torusSOP (par.rows, par.cols, par.radx, par.rady)
  noiseSOP        — deform geometry (par.amplitude, par.period)
  convertSOP      — convert type

CHOPs (signals/audio):
  audioDevInCHOP  — microphone input (par.device=0 for default)
  audioAnalysisCHOP — RMS/peak analysis (par.rms=True, par.peak=True)
  audioSpectrumCHOP — FFT spectrum (par.fftsize)
  noiseCHOP       — noise signal (par.type, par.period)
  mathCHOP        — math ops (par.gain, par.preop, par.postop)
  selectCHOP      — pick channels (par.chop, par.channames)
  timerCHOP       — timer/clock

COMPs:
  cameraCOMP      — camera (par.tz = distance, par.rx/ry/rz = rotation)
  lightCOMP       — light (par.tx/ty/tz = position)
  geoCOMP         — geometry container

CONNECTING AUDIO TO VISUALS (bind expression):
  level.par.brightness.bindExpr = "op('hermes_analysis')['rms'] * 2"
  noise.par.period.bindExpr = "1 + op('hermes_analysis')['rms'] * 4"

3D RENDER PATTERN:
  geo = comp.create(geoCOMP, 'hermes_geo')
  sphere = geo.create(sphereSOP, 'sphere'); sphere.par.rows=60; sphere.par.cols=60
  cam = comp.create(cameraCOMP, 'hermes_cam'); cam.par.tz=3
  light = comp.create(lightCOMP, 'hermes_light'); light.par.ty=2
  render = comp.create(renderTOP, 'hermes_render')
  render.par.w=1920; render.par.h=1080
  render.par.camera=cam.path; render.par.lights=light.path

FEEDBACK TRAILS PATTERN:
  src = comp.create(noiseTOP, 'hermes_src')
  feedback = comp.create(feedbackTOP, 'hermes_feedback')
  blend = comp.create(compositeTOP, 'hermes_blend')
  blend.par.operand = 'add'
  blend.setInputs([src, feedback])
  feedback.par.top = blend.path
  level = comp.create(levelTOP, 'hermes_level')
  level.setInputs([blend]); level.par.contrast = 0.95
  out = comp.create(outTOP, 'hermes_out'); out.setInputs([level])

Generate a complete, working TouchDesigner network. Position nodes in a readable layout
(x: -600 to 600, y: -300 to 300). Always end with an outTOP connected to the main output."""

PROJECT_TYPES = {
    "audio_reactive": ["音響", "音樂", "聲音", "audio", "music", "sound", "節拍", "beat", "頻譜", "spectrum"],
    "interactive": ["互動", "手勢", "觸控", "interactive", "kinect", "gesture", "touch", "mouse", "鍵盤"],
    "particles": ["粒子", "particle", "流體", "fluid", "smoke", "fire", "煙", "火"],
    "geometry_3d": ["3d", "立體", "球體", "幾何", "geometry", "sphere", "mesh", "torus"],
    "data_viz": ["資料", "數據", "data", "visualization", "視覺化"],
    "generative": [],  # default fallback
}


def classify_project_type(description: str) -> str:
    desc_lower = description.lower()
    for ptype, keywords in PROJECT_TYPES.items():
        if any(k in desc_lower for k in keywords):
            return ptype
    return "generative"


def generate_td_project(description: str, project_name: str = "hermes_project") -> dict:
    """Generate TouchDesigner Python code from a natural-language description."""
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    LIVE_CODE_FILE.parent.mkdir(parents=True, exist_ok=True)

    project_type = classify_project_type(description)
    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in project_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2048,
            system=TD_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"Create a TouchDesigner project for: {description}\n"
                    f"Project type hint: {project_type}\n"
                    f"Make it visually impressive and technically correct."
                ),
            }],
        )

        code = response.content[0].text.strip()
        # Strip accidental markdown fences
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:] if lines[-1] != "```" else lines[1:-1])

        header = (
            f"# Hermes TD Project: {safe_name}\n"
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Description: {description}\n"
            f"# Type: {project_type}\n\n"
        )
        full_code = header + code

        project_file = PROJECTS_DIR / f"{safe_name}_{timestamp}.py"
        project_file.write_text(full_code, encoding="utf-8")
        LIVE_CODE_FILE.write_text(full_code, encoding="utf-8")

        meta = {
            "project_name": safe_name,
            "description": description,
            "project_type": project_type,
            "timestamp": timestamp,
            "code_path": str(project_file),
        }
        (PROJECTS_DIR / f"{safe_name}_{timestamp}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        return {
            "success": True,
            "code_path": str(project_file),
            "project_type": project_type,
            "code": full_code,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
