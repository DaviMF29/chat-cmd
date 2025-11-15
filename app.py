"""
Chat CMD - Terminal WebSocket Chat Client
Main entry point for the application.
"""
import asyncio
import argparse
import os

from src.core import config
from src.core.client import connect_to_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WebSocket Chat Client with Image Support')
    parser.add_argument('--sound', '-s', type=str, help='Path to custom notification sound file (.wav)')
    args = parser.parse_args()
    
    # Set notification sound from command line argument or use default
    if args.sound:
        if os.path.exists(args.sound):
            config.NOTIFICATION_SOUND = args.sound
            print(f"Using custom notification sound: {args.sound}")
        else:
            print(f"Warning: Sound file not found at {args.sound}. Using default beep.")
    else:
        # Check for default sound in sounds folder
        default_sound = os.path.join(os.path.dirname(__file__), 'sounds', 'notification.wav')
        if os.path.exists(default_sound) and os.path.getsize(default_sound) > 100:
            config.NOTIFICATION_SOUND = default_sound
            print(f"Using default notification sound: {default_sound}")
    
    try:
        asyncio.run(connect_to_server())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")
