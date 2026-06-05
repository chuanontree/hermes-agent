"""High-level Ableton Live API via AbletonOSC."""
from typing import List, Optional

from .client import AbletonOSCClient


class AbletonLive:
    """Control Ableton Live via the AbletonOSC MIDI Remote Script.

    Requires AbletonOSC installed in Ableton's MIDI Remote Scripts directory
    and selected in Preferences → Link, Tempo & MIDI → MIDI Remote Scripts.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 11000) -> None:
        self._client = AbletonOSCClient(host, send_port=port, recv_port=port + 1)
        self._client.connect()

    # ── Transport ────────────────────────────────────────────────────────────

    def play(self) -> None:
        self._client.send("/live/song/start_playing")

    def stop(self) -> None:
        self._client.send("/live/song/stop_playing")

    def continue_playing(self) -> None:
        self._client.send("/live/song/continue_playing")

    def stop_all_clips(self) -> None:
        self._client.send("/live/song/stop_all_clips")

    # ── Tempo / Time ─────────────────────────────────────────────────────────

    def get_tempo(self) -> Optional[float]:
        r = self._client.query("/live/song/get/tempo")
        return float(r[0]) if r else None

    def set_tempo(self, bpm: float) -> None:
        self._client.send("/live/song/set/tempo", float(bpm))

    def get_position(self) -> Optional[float]:
        r = self._client.query("/live/song/get/current_song_time")
        return float(r[0]) if r else None

    # ── Tracks ───────────────────────────────────────────────────────────────

    def get_num_tracks(self) -> Optional[int]:
        r = self._client.query("/live/song/get/num_tracks")
        return int(r[0]) if r else None

    def get_track_name(self, track_id: int) -> Optional[str]:
        r = self._client.query("/live/track/get/name", track_id)
        return str(r[0]) if r else None

    def get_track_mute(self, track_id: int) -> Optional[bool]:
        r = self._client.query("/live/track/get/mute", track_id)
        return bool(r[0]) if r else None

    def set_track_mute(self, track_id: int, mute: bool) -> None:
        self._client.send("/live/track/set/mute", track_id, int(mute))

    def set_track_volume(self, track_id: int, volume: float) -> None:
        """volume: 0.0 (silent) to 1.0 (0 dB default is ~0.85)"""
        self._client.send("/live/track/set/volume", track_id, float(volume))

    def set_track_pan(self, track_id: int, pan: float) -> None:
        """pan: -1.0 (full left) to 1.0 (full right)"""
        self._client.send("/live/track/set/panning", track_id, float(pan))

    def get_tracks(self) -> List[dict]:
        """Return list of {id, name, muted} for all tracks."""
        n = self.get_num_tracks()
        if n is None:
            return []
        tracks = []
        for i in range(n):
            tracks.append(
                {
                    "id": i,
                    "name": self.get_track_name(i) or f"Track {i + 1}",
                    "muted": self.get_track_mute(i) or False,
                }
            )
        return tracks

    # ── Scenes ───────────────────────────────────────────────────────────────

    def get_num_scenes(self) -> Optional[int]:
        r = self._client.query("/live/song/get/num_scenes")
        return int(r[0]) if r else None

    def get_scene_name(self, scene_id: int) -> Optional[str]:
        r = self._client.query("/live/scene/get/name", scene_id)
        return str(r[0]) if r else None

    def fire_scene(self, scene_id: int) -> None:
        self._client.send("/live/scene/fire", scene_id)

    def get_scenes(self) -> List[dict]:
        """Return list of {id, name} for all scenes."""
        n = self.get_num_scenes()
        if n is None:
            return []
        return [
            {"id": i, "name": self.get_scene_name(i) or f"Scene {i + 1}"}
            for i in range(n)
        ]

    # ── Clips ────────────────────────────────────────────────────────────────

    def fire_clip(self, track_id: int, clip_id: int) -> None:
        self._client.send("/live/clip/fire", track_id, clip_id)

    def stop_clip(self, track_id: int, clip_id: int) -> None:
        self._client.send("/live/clip/stop", track_id, clip_id)

    # ── Recording ────────────────────────────────────────────────────────────

    def get_record_mode(self) -> Optional[bool]:
        r = self._client.query("/live/song/get/record_mode")
        return bool(r[0]) if r else None

    def set_record_mode(self, enabled: bool) -> None:
        self._client.send("/live/song/set/record_mode", int(enabled))

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
