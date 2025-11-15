WEBSOCKET_URI = "wss://b27d072e6b9d.ngrok-free.app"

COMMANDS = {
    "quit": "Exits the interactive terminal. Example: /quit",
    "help": "Displays this list of commands. Example: /help",
    "image": "Sends and displays an image on all terminals. Usage: /image <path/to/file.png>",
    "sound": "Changes the notification sound. Usage: /sound <path/to/sound.wav> | /sound mute | /sound unmute",
    "users": "Lists all online users. Example: /users",
    "clear": "Clears messages for the current user. Example: /clear",
}

NOTIFICATION_SOUND = None
PREVIOUS_NOTIFICATION_SOUND = None
IS_MUTED = False
