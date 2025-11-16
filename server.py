import asyncio
import websockets
import json

USERS = {}

async def handler(websocket):
    user_name = None
    USERS[websocket] = None

    try:
        async for message in websocket:
            print(f"Received: {message}")
            
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
                
                # Handle whisper command
                if data.get('type') == 'whisper':
                    from_user = data.get('from')
                    to_user = data.get('to')
                    message = data.get('message')
                    
                    
                    # Find target user's websocket
                    target_ws = None
                    for ws, username in USERS.items():
                        if username == to_user:
                            target_ws = ws
                            break
                    
                    if target_ws:
                        # Send to target user
                        whisper_msg = json.dumps({
                            "type": "whisper_received",
                            "from": from_user,
                            "message": message
                        })
                        await target_ws.send(whisper_msg)
                        
                        # Send confirmation to sender
                        confirmation = json.dumps({
                            "type": "whisper_sent",
                            "to": to_user,
                            "message": message
                        })
                        await websocket.send(confirmation)
                    else:
                        # User not found
                        print(f"[WHISPER] User '{to_user}' not found")
                        error_msg = json.dumps({
                            "type": "whisper_error",
                            "message": f"User '{to_user}' not found or offline."
                        })
                        await websocket.send(error_msg)
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