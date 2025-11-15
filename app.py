from image import display_image_in_terminal 
import asyncio
import websockets
import sys
import json
import base64
import os
import tempfile
import time
import argparse
import winsound
import threading

# Try to import pygame for MP3 support, fallback to winsound only
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

COMMANDS = {
    "quit": "Exits the interactive terminal. Example: /quit",
    "help": "Displays this list of commands. Example: /help",
    "image": "Sends and displays an image on all terminals. Usage: /image <path/to/file.png>",
    "sound": "Changes the notification sound. Usage: /sound <path/to/sound.wav>",
}

uri = "wss://b27d072e6b9d.ngrok-free.app"

# Global variable for notification sound path
NOTIFICATION_SOUND = None

def play_notification_sound():
    """Play notification sound in a separate thread to avoid blocking"""
    def play():
        try:
            if NOTIFICATION_SOUND and os.path.exists(NOTIFICATION_SOUND):
                # Check if it's an MP3 file and pygame is available
                if NOTIFICATION_SOUND.lower().endswith('.mp3') and PYGAME_AVAILABLE:
                    pygame.mixer.music.load(NOTIFICATION_SOUND)
                    pygame.mixer.music.play()
                    # Wait for the sound to finish playing
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                elif NOTIFICATION_SOUND.lower().endswith('.wav'):
                    winsound.PlaySound(NOTIFICATION_SOUND, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    print(f"\n[WARNING] Unsupported audio format. Please use .wav or .mp3 files.")
                    winsound.MessageBeep(winsound.MB_OK)
            else:
                # Default system beep if no sound file is set
                winsound.MessageBeep(winsound.MB_OK)
                
        except Exception as e:
            pass  # Silently fail if sound cannot be played
    
    threading.Thread(target=play, daemon=True).start()

def render_image_from_data(data):
    try:
        image_bytes = base64.b64decode(data['content'])
        file_name = data['filename']
        
        temp_dir = tempfile.gettempdir()
        unique_id = int(time.time() * 1000)
        temp_path = os.path.join(temp_dir, f"temp_img_{unique_id}_{file_name}")

        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
            
        print(f"\n[{data['user']}] Displaying image '{file_name}'...")
        display_image_in_terminal(temp_path)
        
        os.remove(temp_path)
        
    except Exception as e:
        print(f"\n[ERROR] Failed to render image: {e}")


async def receive_messages(websocket, user_name):
    try:
        async for message_str in websocket:
            try:
                data = json.loads(message_str) 
            except json.JSONDecodeError:
                print(f"\n[SERVER NOTIFICATION] {message_str}")
                sys.stdout.write("> ")
                sys.stdout.flush()
                continue
            
            if data.get("type") == "image_data":
                # Skip rendering if the sender is the current user (already displayed locally)
                if data.get('user') != user_name:
                    play_notification_sound()
                    render_image_from_data(data)
                    sys.stdout.write("> ")
                    sys.stdout.flush()
            
            elif data.get("type") == "message":
                # Skip displaying if the sender is the current user (already displayed locally)
                if data.get('user') != user_name:
                    play_notification_sound()
                    print(f"\r{data.get('user', 'unknown')}: {data.get('text', '')}")
                    sys.stdout.write("> ")
                    sys.stdout.flush()
            
            elif data.get("type") == "notification":
                action = data.get("action", "performed an action")
                print(f"\n[NOTIFICATION] {data.get('user', 'unknown')} {action}.")
            
            elif data.get("type") == "command":
                name = data.get("name", "unknown")
                user = data.get("user", "someone")
                
                if name == "quit":
                    print(f"\n[SERVER] {user} has disconnected.")
                else:
                    print(f"\n[SERVER] Command '{name}' received from {user}.")
            
            else:
                print(f"\n[SERVER] Received unhandled data structure: {data}")
            
            sys.stdout.write("> ")
            sys.stdout.flush()
            
    except websockets.exceptions.ConnectionClosed:
        print("\n[SERVER] Connection closed. Press Enter to exit.")
    except Exception as e:
        print(f"\n[ERROR] An error occurred while receiving data: {e}")

async def send_messages(websocket, user_name):
    
    while True:
        user_input = await asyncio.to_thread(input, "> ")
        user_input = user_input.strip()
        
        if not user_input:
            continue
            
        if user_input.startswith('/'):
            
            parts = user_input.split()
            command_full = parts[0]
            command_name = parts[0].lstrip('/')
            
            
            if command_name == "quit":
                print(f"Goodbye, {user_name}.")
                quit_message = json.dumps({"type": "command", "name": "quit", "user": user_name})
                await websocket.send(quit_message) 
                break
            
            elif command_name == "help":
                print("\n--- AVAILABLE COMMANDS ---")
                for cmd, desc in COMMANDS.items():
                    print(f"/{cmd:<7} : {desc}")
                print("--------------------------\n")
            
            elif command_name == "sound":
                global NOTIFICATION_SOUND
                if len(parts) < 2:
                    print("Usage: /sound <path/to/sound.wav>")
                    print(f"Current sound: {NOTIFICATION_SOUND if NOTIFICATION_SOUND else 'System default beep'}")
                    continue
                
                sound_path = parts[1]
                
                if not os.path.exists(sound_path):
                    print(f"Error: Sound file not found at {sound_path}")
                    continue
                
                NOTIFICATION_SOUND = sound_path
                print(f"Notification sound changed to: {sound_path}")
                play_notification_sound()  # Test the sound
            
            elif command_name == "image":
                if len(parts) < 2:
                    print("Usage: /image <path/to/image>")
                    continue
                    
                image_path = parts[1]
                
                if not os.path.exists(image_path):
                    print(f"Error: File not found at {image_path}")
                    continue
                    
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

            
            else:
                unknown_command = json.dumps({"type": "command", "name": command_name, "user": user_name, "payload": user_input})
                await websocket.send(unknown_command)

        else:
            # Send the message without displaying locally (already visible from input)
            message_data = {"type": "message", "user":user_name, "text": user_input}
            await websocket.send(json.dumps(message_data))
            
    await websocket.close()

async def main_connector():
    try:
        async with websockets.connect(uri) as websocket:
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
        print(f"\n[ERROR] Connection refused. Make sure the server is running at {uri}.")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect or manage tasks: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WebSocket Chat Client with Image Support')
    parser.add_argument('--sound', '-s', type=str, help='Path to custom notification sound file (.wav)')
    args = parser.parse_args()
    
    # Set notification sound from command line argument or use default
    if args.sound:
        if os.path.exists(args.sound):
            NOTIFICATION_SOUND = args.sound
            print(f"Using custom notification sound: {args.sound}")
        else:
            print(f"Warning: Sound file not found at {args.sound}. Using default beep.")
    else:
        # Check for default sound in sounds folder
        default_sound = os.path.join(os.path.dirname(__file__), 'sounds', 'notification.wav')
        if os.path.exists(default_sound) and os.path.getsize(default_sound) > 100:
            NOTIFICATION_SOUND = default_sound
            print(f"Using default notification sound: {default_sound}")
    
    try:
        asyncio.run(main_connector())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")