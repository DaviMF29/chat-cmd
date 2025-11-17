import asyncio
import websockets
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import os
from dotenv import set_key
from src.core import config
from src.handlers.message_handler import receive_messages
from src.handlers.command_handler import process_command


async def send_messages(websocket, user_name, session):
    """Handle sending messages using prompt_toolkit for non-blocking input."""
    while True:
        try:
            user_input = await session.prompt_async("> ")
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
        except (EOFError, KeyboardInterrupt):
            break
            
    await websocket.close()


async def connect_to_server():
    """Connect to the WebSocket server with prompt_toolkit for better terminal handling."""
    try:
        session = PromptSession()

        WEBSOCKET_URI = await session.prompt_async("Enter WebSocket URI to connect in server: ")
        set_key(".env", "WEBSOCKET_URI", WEBSOCKET_URI)

        print(f"Connecting to server at {WEBSOCKET_URI}...")
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            user_name = await session.prompt_async("Enter your name: ")
            print(f"\nWelcome, {user_name}! Type a message or use commands. Type /help for assistance.\n")

            # Use patch_stdout to prevent output from interfering with input
            with patch_stdout():
                send_task = asyncio.create_task(send_messages(websocket, user_name, session))
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
        print(f"\n[ERROR] Connection refused. Make sure the server is running at {WEBSOCKET_URI}.")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect or manage tasks: {e}")
