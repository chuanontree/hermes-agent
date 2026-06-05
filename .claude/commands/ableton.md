---
description: Control Ableton Live via OSC — play/stop, tempo, tracks, scenes, clips
---

You are controlling Ableton Live using the Python CLI at `ableton/`.

Run commands from the repo root with:
```
python3 -m ableton [--host HOST] [--port PORT] <command>
```

## Available commands

| Command | Description |
|---|---|
| `status` | Check connection + show tempo/tracks/scenes |
| `play` | Start playback |
| `stop` | Stop playback |
| `tempo [BPM]` | Get current tempo, or set to BPM |
| `tracks` | List all tracks (id, name, mute state) |
| `scenes` | List all scenes (id, name) |
| `fire-scene <N>` | Launch scene N (0-indexed) |
| `fire-clip <TRACK> <CLIP>` | Trigger clip at track/clip position |
| `mute <N>` | Mute track N |
| `unmute <N>` | Unmute track N |
| `volume <TRACK> <LEVEL>` | Set volume 0.0–1.0 (0.85 = 0 dB) |
| `pan <TRACK> <VALUE>` | Set pan -1.0 (L) to 1.0 (R) |
| `record <on\|off>` | Toggle record mode |

## Python API (for scripts)

```python
from ableton import AbletonLive

with AbletonLive() as live:
    print(live.get_tempo())          # 120.0
    live.set_tempo(140)
    live.play()
    live.fire_scene(0)
    for t in live.get_tracks():
        print(t)                     # {id, name, muted}
```

## First-time setup (if status fails)

1. **Download AbletonOSC** from https://github.com/ideoforms/AbletonOSC/releases
2. **Copy the `AbletonOSC/` folder** into Ableton's MIDI Remote Scripts directory:
   - Mac: `~/Library/Application Support/Ableton/Live x.x/Resources/MIDI Remote Scripts/`
   - Win: `C:\ProgramData\Ableton\Live x.x\Resources\MIDI Remote Scripts\`
3. **Restart Ableton Live**
4. Go to **Preferences → Link, Tempo & MIDI → MIDI Remote Scripts** → select **AbletonOSC**
5. Install Python dependency: `pip install python-osc`

## Workflow rule

Always run `status` first to verify Ableton is reachable before performing any other action.
If status fails, guide the user through the setup steps above.

---

User request: $ARGUMENTS
