import asyncio
import websockets
import json
from src.core import config

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
                    user_life = 100
                    USERS[websocket] = {'name': user_name, 'life': user_life}
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
                elif data.get('type') == 'whisper':
                    from_user = data.get('from')
                    to_user = data.get('to')
                    message = data.get('message')
                    
                    
                    # Find target user's websocket
                    target_ws = None
                    for ws, user in USERS.items():
                        if user["name"] == to_user:
                            target_ws = ws
                            break
                    await websocket.send({"type": "debug", "message": f"Target WS: {target_ws}, To User: {to_user}, From User: {from_user}"})
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
                
                elif data.get('type') == 'atack':
                    from_user = data.get('from')
                    to_user = data.get('to')
                    atack = data.get('atack')
                    
                    # Find target user's websocket
                    target_ws = None
                    for ws, user in USERS.items():
                        if user["name"] == to_user:
                            target_ws = ws
                            break
                    
                    if target_ws:
                        # Send atack to target user
                        atack_msg = json.dumps({
                            "type": "atack_received",
                            "from": from_user,
                            "atack": atack
                        })
                        await target_ws.send(atack_msg)

                        # Send confirmation to sender
                        confirmation = json.dumps({
                            "type": "atack_sent",
                            "to": to_user,
                            "atack": atack
                        })

                        await websocket.send(confirmation)

                        if USERS[target_ws]['life'] > 0:
                            USERS[target_ws]['life'] -= config.ATACKS.get(atack, 0)
                            if USERS[target_ws]['life'] < 0:
                                USERS[target_ws]['life'] = 0

                        life_update = json.dumps({
                            "type": "life_update",
                            "life": USERS[target_ws]['life']
                        })
                        await target_ws.send(life_update)

                        # Notify other users
                        for ws, username in USERS.items():
                            if ws != websocket and ws != target_ws:
                                spectator_msg = json.dumps({
                                    "type": "atack_notification",
                                    "message": f"{from_user} attacked {to_user} with {atack}."
                                })
                                await ws.send(spectator_msg)
                    else:
                        # User not found
                        print(f"[ATACK] User '{to_user}' not found")
                        error_msg = json.dumps({
                            "type": "atack_error",
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