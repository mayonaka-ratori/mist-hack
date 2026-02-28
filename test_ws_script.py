import asyncio
import websockets
import json
import httpx

async def test():
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri, max_size=10_000_000) as websocket:
            print("WebSocket connected successfully")
            
            # Check 4: Japanese mode test
            print("\n--- Check 4: Japanese Mode ---")
            await websocket.send(json.dumps({
                "type": "text",
                "content": "おはよう",
                "language": "ja"
            }))
            print("Sent Japanese message")
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received JSON type: {data['type']}")
                if "translated" in data:
                    print(f"Translated info: {data['translated']}")
                if data["type"] == "image":
                    print("Received image! Japanese flow completed.")
                    break

            # Check 5: English mode test
            print("\n--- Check 5: English Mode ---")
            await websocket.send(json.dumps({
                "type": "text",
                "content": "Good morning I want to pick tomatoes",
                "language": "en"
            }))
            print("Sent English message")
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received JSON type: {data['type']}")
                if "translated" in data:
                    print(f"Translated info: {data['translated']}")
                if data["type"] == "image":
                    print("Received image! English flow completed.")
                    break
            
            # Check 6: Save conversation
            print("\n--- Check 6: Save Conversation ---")
            await websocket.send(json.dumps({
                "type": "end_session"
            }))
            print("Sent end_session message")
            
            print("Checking /history endpoint...")
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:8000/history")
                print(f"/history status code: {resp.status_code}")
                # We expect the HTML template to return
                if "table" in resp.text.lower() or "tbody" in resp.text.lower():
                    print("/history page loaded properly with table structure.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
