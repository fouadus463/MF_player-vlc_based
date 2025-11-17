# mf_player/ui.py
"""Terminal UI: printing and simple input prompts."""
from .util import human_time, clear_screen, safe_get_volume
import os

def print_playlist(files, current_index=0):
    print("Playlist:")
    for i, path in enumerate(files):
        marker = ">" if i == current_index else " "
        print(f" {marker} {i+1:03d}. {os.path.basename(path)}")

def show_ui(player, files, current_index):
    clear_screen()
    try:
        state = player.get_state()
    except Exception:
        state = "UNKNOWN"

    try:
        pos = player.get_time()
        length = player.get_length()
    except Exception:
        pos, length = -1, -1

    vol = safe_get_volume(player)

    print(f"State: {state}   Track: {current_index + 1}/{len(files)}")
    print(f"Time : {human_time(pos)} / {human_time(length)}")
    print(f"Volume: {vol}")
    print("-" * 60)

    for i, path in enumerate(files):
        name = os.path.basename(path)
        marker = ">" if i == current_index else " "
        print(f"{marker} {i+1:03d}. {name}")

    print("-" * 60)
    print("Commands: play | pause | stop | next | prev | v N | v+ | v- | m | pl | exit")
