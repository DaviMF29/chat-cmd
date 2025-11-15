WEBSOCKET_URI = "wss://d7a40b6a955f.ngrok-free.app"

COMMANDS = {
    "quit": "Exits the interactive terminal. Example: /quit",
    "help": "Displays this list of commands. Example: /help",
    "image": "Sends and displays an image on all terminals. Usage: /image <path/to/file.png>",
    "sound": "Changes the notification sound. Usage: /sound <path/to/sound.wav> | /sound mute | /sound unmute",
    "users": "Lists all online users. Example: /users",
    "clear": "Clears messages for the current user. Example: /clear",
    "watch": "Opens a video URL in the default web browser. Usage: /watch <video_url>"
}

NOTIFICATION_SOUND = None
PREVIOUS_NOTIFICATION_SOUND = None
IS_MUTED = False
