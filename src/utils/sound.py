"""Sound notification utilities."""
import os
import time
import threading
import winsound

# Try to import pygame for MP3 support, fallback to winsound only
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def play_notification_sound(sound_path=None):
    """Play notification sound in a separate thread to avoid blocking.
    
    Args:
        sound_path: Path to the sound file. If None, plays system default beep.
    """
    def play():
        try:
            if sound_path and os.path.exists(sound_path):
                # Check if it's an MP3 file and pygame is available
                if sound_path.lower().endswith('.mp3') and PYGAME_AVAILABLE:
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.play()
                    # Wait for the sound to finish playing
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                elif sound_path.lower().endswith('.wav'):
                    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    print(f"\n[WARNING] Unsupported audio format. Please use .wav or .mp3 files.")
                    winsound.MessageBeep(winsound.MB_OK)
            else:
                # Default system beep if no sound file is set
                winsound.MessageBeep(winsound.MB_OK)
                
        except Exception as e:
            pass  # Silently fail if sound cannot be played
    
    threading.Thread(target=play, daemon=True).start()
