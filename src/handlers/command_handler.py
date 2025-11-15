import json
import base64
import os

from src.core import config
from src.utils.sound import play_notification_sound
from src.utils.image_utils import display_image_in_terminal


async def handle_quit_command(websocket, user_name):
    print(f"Goodbye, {user_name}.")
    quit_message = json.dumps({"type": "command", "name": "quit", "user": user_name})
    await websocket.send(quit_message)
    return True


def handle_help_command():
    print("\n--- AVAILABLE COMMANDS ---")
    for cmd, desc in config.COMMANDS.items():
        print(f"/{cmd:<7} : {desc}")
    print("--------------------------\n")


def handle_sound_command(parts):
    if len(parts) < 2:
        print("Usage: /sound <path/to/sound.wav>")
        print(f"Current sound: {config.NOTIFICATION_SOUND if config.NOTIFICATION_SOUND else 'System default beep'}")
        return
    
    sound_path = parts[1]
    
    if not os.path.exists(sound_path):
        print(f"Error: Sound file not found at {sound_path}")
        return
    
    config.NOTIFICATION_SOUND = sound_path
    print(f"Notification sound changed to: {sound_path}")
    play_notification_sound(config.NOTIFICATION_SOUND)  # Test the sound


async def handle_image_command(websocket, user_name, parts):
    if len(parts) < 2:
        print("Usage: /image <path/to/image>")
        return
        
    image_path = parts[1]
    
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        return
        
    print(f"[{user_name}]: Reading and sending image {image_path}...")

    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            
        encoded_content = base64.b64encode(image_bytes).decode('utf-8')
        
        image_data_packet = json.dumps({
            "type": "image_data", 
            "user": user_name, 
            "filename": os.path.basename(image_path),
            "content": encoded_content
        })
        
        await websocket.send(image_data_packet)
        print(f"[{user_name}]: Image packet sent to server.")
        
        print(f"[{user_name}] Displaying image '{os.path.basename(image_path)}'...")
        display_image_in_terminal(image_path)
        
    except Exception as e:
        print(f"Error reading/encoding file: {e}")

async def handle_users_command(websocket, user_name):
    try:
        request = json.dumps({
            "type": "command",
            "name": "users",
            "user": user_name
        })
        await websocket.send(request)
        print("\n[Requesting user list from server...]")
    except Exception as e:
        print(f"\n[ERROR] Failed to request user list: {e}")

async def process_command(websocket, user_name, user_input):
    parts = user_input.split()
    command_name = parts[0].lstrip('/')
    
    if command_name == "quit":
        return await handle_quit_command(websocket, user_name)
    
    elif command_name == "help":
        handle_help_command()
    
    elif command_name == "sound":
        handle_sound_command(parts)
    
    elif command_name == "image":
        await handle_image_command(websocket, user_name, parts)
    
    elif command_name == "users":
        await handle_users_command(websocket, user_name)
    
    else:
        unknown_command = json.dumps({
            "type": "command",
            "name": command_name,
            "user": user_name,
            "payload": user_input
        })
        await websocket.send(unknown_command)
    
    return False
