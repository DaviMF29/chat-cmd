import asyncio
import websockets

USERS = set()
import asyncio
import websockets

USERS = set()

async def handler(websocket):
    USERS.add(websocket)

    try:
        async for message in websocket:
            print(f"Received: {message}")
            
            recipients = [ws for ws in USERS] 

            if recipients:
                send_tasks = [ws.send(message) for ws in recipients]
                # Replace asyncio.wait with asyncio.gather for compatibility with Python 3.8+
                await asyncio.gather(*send_tasks)
                
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Connection closed normally.")
    except Exception as e:
        print(f"Handler error: {e}")
        
    finally:
        USERS.remove(websocket)
        print(f"User disconnected. Total users: {len(USERS)}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")