# mf_player/player.py
"""libVLC wrapper. Keeps VLC-specific calls isolated for testing/mocking."""
import time

try:
    import vlc
except Exception:
    vlc = None

def create_player():
    if vlc is None:
        raise RuntimeError("python-vlc not available")
    inst = vlc.Instance()
    player = inst.media_player_new()
    return inst, player

def play_track(player, instance, path, start_delay=0.25):
    media = instance.media_new(path)
    player.set_media(media)
    player.play()
    time.sleep(start_delay)

def pause(player):
    player.pause()

def stop(player):
    player.stop()

def set_volume(player, n):
    player.audio_set_volume(max(0, min(100, int(n))))

# Read helpers — thin wrappers
def get_time(player):
    return player.get_time()

def get_length(player):
    return player.get_length()

def get_state(player):
    return str(player.get_state())

def audio_get_volume(player):
    return player.audio_get_volume()

def audio_get_mute(player):
    return player.audio_get_mute()

def audio_set_mute(player, flag):
    return player.audio_set_mute(flag)
