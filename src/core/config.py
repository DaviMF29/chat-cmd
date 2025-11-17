COMMANDS = {
    "quit": "Exits the interactive terminal. Example: /quit",
    "help": "Displays this list of commands. Example: /help",
    "image": "Sends and displays an image on all terminals. Usage: /image <path/to/file.png>",
    "sound": "Changes the notification sound. Usage: /sound <path/to/sound.wav> | /sound mute | /sound unmute",
    "users": "Lists all online users. Example: /users",
    "clear": "Clears messages for the current user. Example: /clear",
    "watch": "Opens a video URL in the default web browser. Usage: /watch <video_url>",
    "whisper": "Sends a private message to a specific user. Usage: /whisper <username> <message>",
    "atack": "Sends an atack command to a specific user. Usage: /atack <username> <atack>",
}

ATACKS = {
    "fireball": 20,
    "punch": 8,
    "ice_shard": 15,
    "lightning": 18,
    "earthquake": 25,
    "wind_slash": 12,
    "water_blast": 14,
    "shadow_strike": 22,
    "holy_light": 19,
    "poison_dart": 10,
    "rock_throw": 13,
    "flame_wave": 17,
    "thunder_clap": 16,
    "blizzard": 21,
    "venom_spit": 11,
    "meteor": 30,
    "energy_burst": 24,
    "dark_pulse": 23,
    "solar_flare": 26,
    "gravity_crush": 28
}

NOTIFICATION_SOUND = None
PREVIOUS_NOTIFICATION_SOUND = None
IS_MUTED = False
