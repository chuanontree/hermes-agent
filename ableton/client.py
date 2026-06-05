"""Low-level OSC client for AbletonOSC MIDI Remote Script."""
import socket
import threading
import time
from typing import Dict, List, Optional

from pythonosc.osc_message import OscMessage
from pythonosc.osc_message_builder import OscMessageBuilder


class AbletonOSCClient:
    """UDP socket that sends OSC messages to AbletonOSC and receives responses.

    AbletonOSC replies to the UDP source address of every request, so binding
    to recv_port and sending from that same socket ensures responses arrive here.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        send_port: int = 11000,
        recv_port: int = 11001,
    ) -> None:
        self.host = host
        self.send_port = send_port
        self.recv_port = recv_port
        self._responses: Dict[str, List] = {}
        self._lock = threading.Lock()
        self._running = False
        self._sock: Optional[socket.socket] = None
        self._recv_thread: Optional[threading.Thread] = None

    def connect(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(("", self.recv_port))
        self._sock.settimeout(0.1)
        self._running = True
        self._recv_thread = threading.Thread(
            target=self._recv_loop, daemon=True, name="ableton-osc-recv"
        )
        self._recv_thread.start()

    def _recv_loop(self) -> None:
        while self._running:
            try:
                data, _ = self._sock.recvfrom(65535)
                msg = OscMessage(data)
                with self._lock:
                    self._responses[msg.address] = list(msg.params)
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception:
                continue

    def send(self, address: str, *args) -> None:
        builder = OscMessageBuilder(address=address)
        for arg in args:
            builder.add_arg(arg)
        self._sock.sendto(builder.build().dgram, (self.host, self.send_port))

    def query(self, address: str, *args, timeout: float = 2.0) -> Optional[List]:
        """Send an OSC message and wait for a response on the same address."""
        with self._lock:
            self._responses.pop(address, None)

        self.send(address, *args)

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                if address in self._responses:
                    return self._responses[address]
            time.sleep(0.01)
        return None

    def close(self) -> None:
        self._running = False
        if self._sock:
            self._sock.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()
