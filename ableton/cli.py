"""CLI for controlling Ableton Live via AbletonOSC."""
import argparse
import sys

from .api import AbletonLive


# ── Command handlers ──────────────────────────────────────────────────────────

def cmd_status(live: AbletonLive, _args) -> int:
    tempo = live.get_tempo()
    if tempo is None:
        print("ERROR: Cannot reach Ableton Live.")
        print("")
        print("Checklist:")
        print("  1. Ableton Live is open")
        print("  2. AbletonOSC is in the MIDI Remote Scripts folder")
        print("     Mac:  ~/Library/Application Support/Ableton/Live x.x/Resources/MIDI Remote Scripts/AbletonOSC")
        print("     Win:  C:\\ProgramData\\Ableton\\Live x.x\\Resources\\MIDI Remote Scripts\\AbletonOSC")
        print("  3. AbletonOSC is enabled: Ableton → Preferences → Link, Tempo & MIDI")
        print("     → MIDI Remote Scripts → select AbletonOSC")
        return 1

    pos = live.get_position()
    num_tracks = live.get_num_tracks()
    num_scenes = live.get_num_scenes()

    print("Ableton Live — Connected")
    print(f"  Tempo   : {tempo:.2f} BPM")
    if pos is not None:
        print(f"  Position: bar {int(pos) + 1}")
    if num_tracks is not None:
        print(f"  Tracks  : {num_tracks}")
    if num_scenes is not None:
        print(f"  Scenes  : {num_scenes}")
    return 0


def cmd_play(live: AbletonLive, _args) -> int:
    live.play()
    print("Playing")
    return 0


def cmd_stop(live: AbletonLive, _args) -> int:
    live.stop()
    print("Stopped")
    return 0


def cmd_tempo(live: AbletonLive, args) -> int:
    if args.bpm is not None:
        live.set_tempo(args.bpm)
        print(f"Tempo set to {args.bpm} BPM")
    else:
        t = live.get_tempo()
        if t is None:
            print("ERROR: Could not get tempo — is Ableton running?")
            return 1
        print(f"{t:.2f} BPM")
    return 0


def cmd_tracks(live: AbletonLive, _args) -> int:
    tracks = live.get_tracks()
    if not tracks:
        print("ERROR: Could not get tracks")
        return 1
    print(f"Tracks ({len(tracks)}):")
    for t in tracks:
        mute_tag = " [muted]" if t["muted"] else ""
        print(f"  {t['id']:>3}  {t['name']}{mute_tag}")
    return 0


def cmd_scenes(live: AbletonLive, _args) -> int:
    scenes = live.get_scenes()
    if not scenes:
        print("ERROR: Could not get scenes")
        return 1
    print(f"Scenes ({len(scenes)}):")
    for s in scenes:
        print(f"  {s['id']:>3}  {s['name']}")
    return 0


def cmd_fire_scene(live: AbletonLive, args) -> int:
    live.fire_scene(args.scene_id)
    print(f"Fired scene {args.scene_id}")
    return 0


def cmd_fire_clip(live: AbletonLive, args) -> int:
    live.fire_clip(args.track_id, args.clip_id)
    print(f"Fired clip {args.clip_id} on track {args.track_id}")
    return 0


def cmd_mute(live: AbletonLive, args) -> int:
    live.set_track_mute(args.track_id, True)
    print(f"Track {args.track_id} muted")
    return 0


def cmd_unmute(live: AbletonLive, args) -> int:
    live.set_track_mute(args.track_id, False)
    print(f"Track {args.track_id} unmuted")
    return 0


def cmd_volume(live: AbletonLive, args) -> int:
    if not 0.0 <= args.level <= 1.0:
        print("ERROR: Volume must be between 0.0 and 1.0")
        return 1
    live.set_track_volume(args.track_id, args.level)
    print(f"Track {args.track_id} volume → {args.level:.2f}")
    return 0


def cmd_pan(live: AbletonLive, args) -> int:
    if not -1.0 <= args.value <= 1.0:
        print("ERROR: Pan must be between -1.0 and 1.0")
        return 1
    live.set_track_pan(args.track_id, args.value)
    print(f"Track {args.track_id} pan → {args.value:.2f}")
    return 0


def cmd_record(live: AbletonLive, args) -> int:
    enabled = args.state.lower() in ("on", "1", "true")
    live.set_record_mode(enabled)
    print(f"Record mode {'ON' if enabled else 'OFF'}")
    return 0


# ── Argument parser ───────────────────────────────────────────────────────────

HANDLERS = {
    "status": cmd_status,
    "play": cmd_play,
    "stop": cmd_stop,
    "tempo": cmd_tempo,
    "tracks": cmd_tracks,
    "scenes": cmd_scenes,
    "fire-scene": cmd_fire_scene,
    "fire-clip": cmd_fire_clip,
    "mute": cmd_mute,
    "unmute": cmd_unmute,
    "volume": cmd_volume,
    "pan": cmd_pan,
    "record": cmd_record,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ableton",
        description="Control Ableton Live via AbletonOSC",
    )
    p.add_argument("--host", default="127.0.0.1", help="AbletonOSC host (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=11000, help="AbletonOSC send port (default: 11000)")

    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show Ableton Live status and verify connection")
    sub.add_parser("play", help="Start playback")
    sub.add_parser("stop", help="Stop playback")

    p_tempo = sub.add_parser("tempo", help="Get or set tempo in BPM")
    p_tempo.add_argument("bpm", type=float, nargs="?", help="BPM to set (omit to read)")

    sub.add_parser("tracks", help="List all tracks")
    sub.add_parser("scenes", help="List all scenes")

    p_fs = sub.add_parser("fire-scene", help="Launch a scene by index")
    p_fs.add_argument("scene_id", type=int, help="Scene index (0-based)")

    p_fc = sub.add_parser("fire-clip", help="Trigger a specific clip")
    p_fc.add_argument("track_id", type=int, help="Track index (0-based)")
    p_fc.add_argument("clip_id", type=int, help="Clip index (0-based)")

    p_mute = sub.add_parser("mute", help="Mute a track")
    p_mute.add_argument("track_id", type=int, help="Track index (0-based)")

    p_unmute = sub.add_parser("unmute", help="Unmute a track")
    p_unmute.add_argument("track_id", type=int, help="Track index (0-based)")

    p_vol = sub.add_parser("volume", help="Set track volume (0.0–1.0)")
    p_vol.add_argument("track_id", type=int)
    p_vol.add_argument("level", type=float, help="0.0 = silent, 0.85 = 0 dB, 1.0 = max")

    p_pan = sub.add_parser("pan", help="Set track pan (-1.0 left … 1.0 right)")
    p_pan.add_argument("track_id", type=int)
    p_pan.add_argument("value", type=float)

    p_rec = sub.add_parser("record", help="Toggle record mode")
    p_rec.add_argument("state", choices=["on", "off", "1", "0", "true", "false"])

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        live = AbletonLive(host=args.host, port=args.port)
    except OSError as exc:
        print(f"ERROR: Could not bind receive port {args.port + 1}: {exc}")
        print("Another instance may already be running.")
        sys.exit(1)

    try:
        handler = HANDLERS.get(args.command)
        if handler:
            sys.exit(handler(live, args))
        else:
            parser.print_help()
            sys.exit(1)
    finally:
        live.close()


if __name__ == "__main__":
    main()
