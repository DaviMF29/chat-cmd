import json
import base64
import os
from collections import defaultdict
import cv2
from src.core import config
from src.utils.sound import play_notification_sound
from src.utils.image_utils import display_image_in_terminal
import subprocess

# Ensure user_messages is initialized globally
user_messages = defaultdict(list)

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
        print("Usage: /sound <path/to/sound.wav> | /sound mute | /sound unmute")
        status = "muted" if config.IS_MUTED else (config.NOTIFICATION_SOUND if config.NOTIFICATION_SOUND else "System default beep")
        print(f"Current sound: {status}")
        return
    
    sound_arg = parts[1]
    
    if sound_arg.lower() == "mute":
        if not config.IS_MUTED:
            config.PREVIOUS_NOTIFICATION_SOUND = config.NOTIFICATION_SOUND
            config.IS_MUTED = True
            print("Notification sound muted.")
        else:
            print("Notification sound is already muted.")
        return
    
    elif sound_arg.lower() == "unmute":
        if config.IS_MUTED:
            config.IS_MUTED = False
            config.NOTIFICATION_SOUND = config.PREVIOUS_NOTIFICATION_SOUND
            status = config.NOTIFICATION_SOUND if config.NOTIFICATION_SOUND else "System default beep"
            print(f"Notification sound unmuted: {status}")
        else:
            print("Notification sound is not muted.")
        return

    path = "sounds/"+sound_arg
    if not os.path.exists(path):
        print(f"Error: Sound file not found at {path}")
        return
    
    config.NOTIFICATION_SOUND = sound_arg
    config.IS_MUTED = False
    print(f"Notification sound changed to: {sound_arg}")
    play_notification_sound(config.NOTIFICATION_SOUND) 


async def handle_image_command(websocket, user_name, parts):
    if len(parts) < 2:
        print("Usage: /image <path/to/image>")
        return
        
    image_path = "images/"+parts[1]
    
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        return
        
    print(f"[{user_name}]: Reading and sending image {image_path}...")

    try:
        import sys
        
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
        
        # Display image locally using the same method as receiving
        sys.__stdout__.write(f"[{user_name}] Displaying image '{os.path.basename(image_path)}'...\n")
        sys.__stdout__.flush()
        
        # Temporarily redirect stdout to real stdout to bypass prompt_toolkit
        old_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        try:
            display_image_in_terminal(image_path)
        finally:
            sys.stdout = old_stdout
        
        sys.__stdout__.write("\n")
        sys.__stdout__.flush()
        
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

def handle_clear_messages(user_name):
    os.system('cls' if os.name == 'nt' else 'clear')
    if user_name in user_messages:
        user_messages[user_name].clear()
    print(f"[{user_name}] Cleared the terminal.\n")

def store_message(user_name, message):
    user_messages[user_name].append(message)

def handle_watch_video(parts, user_name):
    import webbrowser
    video_url = parts[1]
    
    try:
        print(f"[{user_name}] Opening video in browser: {video_url}")
        webbrowser.open(video_url)
        print(f"[{user_name}] Video opened successfully.")
    except Exception as e:
        print(f"Error opening video: {e}")

async def handle_whisper_command(websocket, user_name, parts):
    if len(parts) < 3:
        print("Usage: /whisper <username> <message>")
        return
    
    target_user = parts[1]
    message = ' '.join(parts[2:])
    
    whisper_data = json.dumps({
        "type": "whisper",
        "from": user_name,
        "to": target_user,
        "message": message
    })
    
    await websocket.send(whisper_data)
    print(f"[Whisper to {target_user}] {message}")

async def handle_atack_command(websocket, user_name, parts):
    if len(parts) < 3:
        print("Usage: /atack <username> <atack")
        return
    
    target_user = parts[1]
    atack = parts[2]
    if atack not in config.ATACKS:
        print(f"Error: Unknown atack '{atack}'. Available atacks: {', '.join(config.ATACKS.keys())}")
        return
    
    atack_data = json.dumps({
        "type": "atack",
        "from": user_name,
        "to": target_user,
        "atack": atack
    })
    
    await websocket.send(atack_data)
    print(f"You hit {target_user} with {atack}.")
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
        return False

    elif command_name == "clear":
        handle_clear_messages(user_name)
        return False
    
    elif command_name == "watch":
        handle_watch_video(parts, user_name)
        return False
    
    elif command_name == "whisper":
        await handle_whisper_command(websocket, user_name, parts)
        return False
    
    elif command_name == "atack":
        await handle_atack_command(websocket, user_name, parts)
        return False

    # Store the message for the user
    user_messages[user_name].append(user_input)
    
    unknown_command = json.dumps({
        "type": "command",
        "name": command_name,
        "user": user_name,
        "payload": user_input
    })
    await websocket.send(unknown_command)
    
    return False
