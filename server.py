import asyncio
import websockets
import json

# Store websockets with their usernames
USERS = {}  # {websocket: username}

async def handler(websocket):
    user_name = None
    USERS[websocket] = None  # Initially no username

    try:
        async for message in websocket:
            print(f"Received: {message}")
            
            # Try to parse message to extract username
            try:
                data = json.loads(message)
                
                # Store username on first message
                if USERS[websocket] is None and data.get('user'):
                    user_name = data.get('user')
                    USERS[websocket] = user_name
                    print(f"User '{user_name}' registered. Total users: {len([u for u in USERS.values() if u])}")
                
                # Handle users command
                if data.get('type') == 'command' and data.get('name') == 'users':
                    online_users = [name for name in USERS.values() if name]
                    response = json.dumps({
                        "type": "user_list",
                        "users": online_users,
                        "count": len(online_users)
                    })
                    await websocket.send(response)
                    continue
                    
            except json.JSONDecodeError:
                pass  # Not JSON, treat as regular message
            
            # Broadcast to all users
            recipients = [ws for ws in USERS.keys()] 

            if recipients:
                send_tasks = [ws.send(message) for ws in recipients]
                await asyncio.gather(*send_tasks, return_exceptions=True)
                
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Connection closed normally.")
    except Exception as e:
        print(f"Handler error: {e}")
        
    finally:
        if websocket in USERS:
            disconnected_user = USERS[websocket]
            del USERS[websocket]
            print(f"User '{disconnected_user}' disconnected. Total users: {len([u for u in USERS.values() if u])}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")