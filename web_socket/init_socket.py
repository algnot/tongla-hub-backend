import asyncio
import websockets
from util.config import set_config

active_sessions = {}


async def private_channel(websocket, channel_id):
    if channel_id not in active_sessions:
        active_sessions[channel_id] = []

    active_sessions[channel_id].append(websocket)
    try:
        async for message in websocket:
            print(f"[{channel_id}] {message}")

            for client in active_sessions[channel_id]:
                if client != websocket:
                    await client.send(message)

    finally:
        active_sessions[channel_id].remove(websocket)
        if not active_sessions[channel_id]:
            del active_sessions[channel_id]

async def handler(websocket):
    channel_id = websocket.request.path.split('/')[1]
    if not channel_id:
        await websocket.close()
        return

    await private_channel(websocket, channel_id)

async def init_web_socket_server():
    server_port = set_config("SOCKET_PORT", "9001")
    async with websockets.serve(handler, "0.0.0.0", int(server_port)):
        print("WebSocket server is started")
        await asyncio.Future()
