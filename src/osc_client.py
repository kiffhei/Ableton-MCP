"""
osc_client.py — Ableton Live MCP Server
Cliente OSC para comunicación bidireccional con AbletonOSC.
"""

import logging
import threading
from typing import Any

from pythonosc import udp_client, dispatcher, osc_server

logger = logging.getLogger("ableton-mcp")

ABLETON_HOST = "127.0.0.1"
ABLETON_SEND_PORT = 11000   # Puerto donde Ableton escucha
ABLETON_RECV_PORT = 11001   # Puerto donde recibimos respuestas

osc_client: udp_client.SimpleUDPClient | None = None
osc_responses: dict[str, Any] = {}
osc_lock = threading.Lock()


def init_osc_client():
    global osc_client
    osc_client = udp_client.SimpleUDPClient(ABLETON_HOST, ABLETON_SEND_PORT)
    logger.info(f"OSC client → {ABLETON_HOST}:{ABLETON_SEND_PORT}")


def send_osc(address: str, *args):
    """Envía un mensaje OSC a Ableton."""
    if osc_client is None:
        init_osc_client()
    logger.info(f"OSC → {address} {args}")
    osc_client.send_message(address, list(args))


def osc_response_handler(address, *args):
    with osc_lock:
        osc_responses[address] = args
    logger.info(f"OSC ← {address}: {args}")


def start_osc_listener():
    """Inicia listener para respuestas de Ableton."""
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(osc_response_handler)
    server = osc_server.ThreadingOSCUDPServer(
        (ABLETON_HOST, ABLETON_RECV_PORT), disp
    )
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    logger.info(f"OSC listener en puerto {ABLETON_RECV_PORT}")
