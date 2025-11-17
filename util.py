# mf_player/util.py
"""Small helpers and safe wrappers for libVLC quirks."""
import os
import time

def human_time(ms):
    if not ms or ms <= 0:
        return "--:--"
    secs = int(ms // 1000)
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

# libVLC-safe wrappers
def safe_get_volume(player, default=50):
    try:
        v = player.audio_get_volume()
        if v is None or (isinstance(v, int) and v < 0):
            return default
        return int(v)
    except Exception:
        return default

def safe_get_mute(player):
    try:
        return bool(player.audio_get_mute())
    except Exception:
        return False

def safe_set_volume(player, value):
    try:
        val = int(value)
        val = max(0, min(100, val))
        player.audio_set_volume(val)
        time.sleep(0.05)
        return safe_get_volume(player)
    except Exception:
        return None

def safe_stop(player, delay=0.12):
    try:
        player.stop()
    except Exception:
        pass
    time.sleep(delay)
