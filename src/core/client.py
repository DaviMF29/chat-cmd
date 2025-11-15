import asyncio
import websockets
import json

from src.core import config
from src.handlers.message_handler import receive_messages
from src.handlers.command_handler import process_command


async def send_messages(websocket, user_name):
    while True:
        user_input = await asyncio.to_thread(input, "> ")
        user_input = user_input.strip()
        
        if not user_input:
            continue
            
        if user_input.startswith('/'):
            should_exit = await process_command(websocket, user_name, user_input)
            if should_exit:
                break
        else:
            message_data = {
                "type": "message",
                "user": user_name,
                "text": user_input
            }
            await websocket.send(json.dumps(message_data))
            
    await websocket.close()


async def connect_to_server():
    try:
        async with websockets.connect(config.WEBSOCKET_URI) as websocket:
            user_name = await asyncio.to_thread(input, "Enter your name: ")
            print(f"\nWelcome, {user_name}! Type a message or use commands. Type /help for assistance.")

            send_task = asyncio.create_task(send_messages(websocket, user_name))
            receive_task = asyncio.create_task(receive_messages(websocket, user_name))
            
            await asyncio.wait(
                [send_task, receive_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            
            if not send_task.done():
                send_task.cancel()
            if not receive_task.done():
                receive_task.cancel()
            
    except ConnectionRefusedError:
        print(f"\n[ERROR] Connection refused. Make sure the server is running at {config.WEBSOCKET_URI}.")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect or manage tasks: {e}")
