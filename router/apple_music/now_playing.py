from flask import Blueprint, jsonify, Response
from util.config import get_config
from util.request import handle_error, fetch_and_convert_image_to_base64
import websockets
import ssl
import json
import os
import html
import time
import asyncio

from util.time import format_time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

now_playing_app = Blueprint("now_playing", __name__)

latest_song = {}

ssl_context = ssl._create_unverified_context()

@now_playing_app.route("/now-playing.svg", methods=["GET"])
@handle_error
def get_now_playing_svg():
    content = ""
    with open(f"{BASE_DIR}/static/now_playing.svg", "r", encoding="utf-8") as f:
        content = f.read()
        content = content.replace("{info@artist}", html.escape(latest_song.get("artist", "")))
        content = content.replace("{info@title}", html.escape(latest_song.get("title", "")))
        base64_img = fetch_and_convert_image_to_base64(latest_song.get("albumArt", ""))
        content = content.replace("{info@image}", html.escape(base64_img))

        start_ts = latest_song.get("startTimestamp", 0)
        end_ts = latest_song.get("endTimestamp", 1000)
        now_ts = time.time() * 1000
        duration_ms = end_ts - start_ts
        elapsed_ms = now_ts - start_ts

        progress_percent = min(100.0, max(0.0, (elapsed_ms / duration_ms) * 100.0))

        elapsed_text = format_time(elapsed_ms)
        remaining_text = "-" + format_time(end_ts - now_ts if now_ts > start_ts else 0)
        progress_percent_text = f"{progress_percent:.2}%"

        content = content.replace("{info@elapsed}", elapsed_text)
        content = content.replace("{info@remaining}", remaining_text)
        content = content.replace("{info@progress_percent}", progress_percent_text)

    return Response(content, mimetype="image/svg+xml", headers={"Content-Length": str(len(content))})

@now_playing_app.route("/now-playing.json", methods=["GET"])
@handle_error
def get_now_playing_json():
    return jsonify(latest_song)


async def connect_websocket():
    global latest_song
    while True:
        try:
            print("Trying to connect to WebSocket...")
            uri = get_config("APPLE_MUSIC_SOCKET_HOST", "wss://localhost")
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                print("Connected to WebSocket")
                while True:
                    message = await websocket.recv()
                    try:
                        latest_song = json.loads(message)
                    except json.JSONDecodeError:
                        print("Invalid JSON:", message)
        except Exception as e:
            print("WebSocket Error:", e)
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
