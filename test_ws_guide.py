import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "type": "text",
            "content": "トマトはおいしいね。"
        }))
        
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            if data["type"] == "instant":
                print(f"[TEST CLIENT] Received instant payload: {json.dumps(data, ensure_ascii=False)}")
                break

asyncio.run(test())
