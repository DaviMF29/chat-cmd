import os
import sys
import time
import threading
import platform

if platform.system() == 'Windows':
    import winsound
    WINSOUND_AVAILABLE = True
else:
    WINSOUND_AVAILABLE = False

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def is_terminal_focused():
    try:
        if platform.system() == 'Windows':
            import ctypes
            from ctypes import wintypes

            hwnd = ctypes.windll.user32.GetForegroundWindow()

            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            current_pid = os.getpid()

            return pid.value == current_pid

        elif platform.system() == 'Linux':
            import subprocess
            try:
                result = subprocess.run(
                    ['xdotool', 'getactivewindow', 'getwindowpid'],
                    capture_output=True,
                    text=True,
                    timeout=0.5
                )
                if result.returncode == 0:
                    active_pid = int(result.stdout.strip())
                    current_pid = os.getpid()
                    return active_pid == current_pid
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                pass

            return True
        else:
            return True

    except Exception:
        return True


def play_notification_sound(sound_path=None):
    if is_terminal_focused():
        return

    def play():
        try:
            if sound_path and os.path.exists(sound_path):
                if PYGAME_AVAILABLE:
                    if sound_path.lower().endswith(('.mp3', '.wav', '.ogg')):
                        pygame.mixer.music.load(sound_path)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                    else:
                        print(f"\n[WARNING] Unsupported audio format. Please use .wav, .mp3, or .ogg files.")
                        _play_system_beep()
                elif WINSOUND_AVAILABLE and sound_path.lower().endswith('.wav'):
                    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    _play_system_beep()
            else:
                _play_system_beep()

        except Exception as e:
            pass

    threading.Thread(target=play, daemon=True).start()


def _play_system_beep():
    try:
        if WINSOUND_AVAILABLE:
            winsound.MessageBeep(winsound.MB_OK)
        else:
            sys.stdout.write('\a')
            sys.stdout.flush()
    except Exception:
        pass
