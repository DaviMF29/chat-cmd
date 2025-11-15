"""Message handling for WebSocket communication."""
import sys
import json
import base64
import os
import tempfile
import time
import websockets

from src.utils.sound import play_notification_sound
from src.utils.image_utils import display_image_in_terminal
from src.core import config


def render_image_from_data(data):
    """Render an image received from websocket data.
    
    Args:
        data: Dictionary containing image data with 'content', 'filename', and 'user'.
    """
    try:
        image_bytes = base64.b64decode(data['content'])
        file_name = data['filename']
        
        temp_dir = tempfile.gettempdir()
        unique_id = int(time.time() * 1000)
        temp_path = os.path.join(temp_dir, f"temp_img_{unique_id}_{file_name}")

        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
            
        # Write directly to real stdout to bypass prompt_toolkit
        sys.__stdout__.write(f"\n[{data['user']}] Displaying image '{file_name}'...\n")
        sys.__stdout__.flush()
        
        # Use the original display function but redirect to real stdout
        old_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        try:
            display_image_in_terminal(temp_path)
        finally:
            sys.stdout = old_stdout
        
        sys.__stdout__.write("\n")
        sys.__stdout__.flush()
        
        os.remove(temp_path)
        
    except Exception as e:
        print(f"\n[ERROR] Failed to render image: {e}")


async def receive_messages(websocket, user_name):
    """Receive and handle messages from the WebSocket server.
    
    Args:
        websocket: WebSocket connection object.
        user_name: Current user's name.
    """
    try:
        async for message_str in websocket:
            try:
                data = json.loads(message_str) 
            except json.JSONDecodeError:
                print(f"[SERVER NOTIFICATION] {message_str}")
                continue
            
            if data.get("type") == "image_data":
                # Skip rendering if the sender is the current user (already displayed locally)
                if data.get('user') != user_name:
                    play_notification_sound(config.NOTIFICATION_SOUND)
                    render_image_from_data(data)
            
            elif data.get("type") == "message":
                # Skip displaying if the sender is the current user (already displayed locally)
                if data.get('user') != user_name:
                    play_notification_sound(config.NOTIFICATION_SOUND)
                    print(f"{data.get('user', 'unknown')}: {data.get('text', '')}")
            
            elif data.get("type") == "notification":
                action = data.get("action", "performed an action")
                print(f"[NOTIFICATION] {data.get('user', 'unknown')} {action}.")
            
            elif data.get("type") == "command":
                name = data.get("name", "unknown")
                user = data.get("user", "someone")
                
                if name == "quit":
                    print(f"\n[SERVER] {user} has disconnected.")
                else:
                    print(f"\n[SERVER] Command '{name}' received from {user}.")
            
            elif data.get("type") == "user_list":
                # Display online users
                users = data.get("users", [])
                count = data.get("count", 0)
                print(f"\n--- ONLINE USERS ({count}) ---")
                for user in users:
                    indicator = " (you)" if user == user_name else ""
                    print(f"  • {user}{indicator}")
                print("---------------------------")
            
            else:
                print(f"[SERVER] Received unhandled data structure: {data}")
            
    except websockets.exceptions.ConnectionClosed:
        print("\n[SERVER] Connection closed. Press Enter to exit.")
    except Exception as e:
        print(f"\n[ERROR] An error occurred while receiving data: {e}")
