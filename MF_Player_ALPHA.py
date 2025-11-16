#!/usr/bin/env python3
"""
MF_Player_ALPHA.py — refactored so each function uses only local variables
or values passed in as parameters (no module-level state except imports).

Place this file as MF_Player_ALPHA.py and run with:
    python MF_Player_ALPHA.py /path/to/media
or
    python MF_Player_ALPHA.py
which will default to ./audio in the cwd.
"""

import os
import sys
import time

# Try to import python-vlc; if it fails, give a clear message and stop.
try:
    import vlc
except Exception:
    print("MF_Player can't find or load python-vlc (libVLC).")
    if os.name == "nt":
        print("Install system VLC and python-vlc, e.g.:")
        print("Download vlc.exe & install it from : videolan ")
        print("in cmd [ pip install python-vlc ]")
    else:
        print("Install system vlc and python-vlc, e.g.:")
        print(" ubuntu : sudo apt install vlc, Arch : sudo pacman -S vlc")
        print("  pip install python-vlc")
    sys.exit(1)


# ---------------------------
# Utility helpers (pure/local)
# ---------------------------

def human_time(ms):
    """Convert milliseconds to H:MM:SS or MM:SS. Return '--:--' if unknown."""
    if not ms or ms <= 0:
        return "--:--"
    seconds = int(ms // 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def clear_screen():
    """Clear terminal screen (cross-platform)."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# ---------------------------
# Playlist helpers
# ---------------------------

def get_media_folder_from_args(argv):
    """
    Return media folder path derived from argv (list of args).
    This function no longer reads sys.argv by itself; it uses only the argv parameter.
    """
    if len(argv) > 1:
        return argv[1]
    return os.path.join(os.getcwd(), "audio")


def find_media_files(folder, allowed_ext):
    """
    Return sorted list of media file paths inside `folder` matching `allowed_ext`.
    This function uses only its parameters and local variables.
    If folder missing or no files found, it raises ValueError — caller decides what to do.
    """
    if not os.path.isdir(folder):
        raise ValueError(f"Folder not found: {folder}")

    files = []
    for name in os.listdir(folder):
        full = os.path.join(folder, name)
        # local variables only: full, name
        if os.path.isfile(full) and full.lower().endswith(allowed_ext):
            files.append(full)

    files.sort()
    if not files:
        raise ValueError(f"No media files found in: {folder}")
    return files


def print_playlist(files, current_index=0):
    """Print playlist to stdout. Uses only params and local loop variables."""
    print("Playlist:")
    for i, path in enumerate(files):
        marker = ">" if i == current_index else " "
        print(f" {marker} {i+1:03d}. {os.path.basename(path)}")


# ---------------------------
# VLC / Player helpers
# ---------------------------

def create_vlc_player():
    """
    Create and return a (instance, player) tuple.
    Uses only local variables and the vlc module imported at top-level.
    """
    inst = vlc.Instance()
    player = inst.media_player_new()
    return inst, player


def play_track(player, instance, path, start_delay=0.3):
    """
    Load the path into the provided player and start playback.
    Uses only the parameters and local variables.
    """
    media = instance.media_new(path)
    player.set_media(media)
    player.play()
    time.sleep(start_delay)


def clamp_index(index, n):
    """
    Wrap index into [0, n-1] using modulo. If n <= 0, return 0.
    Pure function using only inputs.
    """
    if n <= 0:
        return 0
    return index % n


# ---------------------------
# UI / display
# ---------------------------

def show_ui(player, files, current_index):
    """
    Clear screen and show:
      - current state, time, volume
      - playlist with marker on current_index
    This function reads from the passed `player` and uses only local variables.
    """
    clear_screen()

    # read state, time, length - tolerate exceptions and use local fallbacks
    try:
        state = str(player.get_state())
    except Exception:
        state = "UNKNOWN"

    try:
        pos = player.get_time()
        length = player.get_length()
    except Exception:
        pos = -1
        length = -1

    try:
        vol = player.audio_get_volume()
    except Exception:
        vol = "?"

    # display header
    print(f"State: {state}   Track: {current_index + 1}/{len(files)}")
    print(f"Time : {human_time(pos)} / {human_time(length)}")
    print(f"Volume: {vol}")
    print("-" * 60)

    # playlist (local loop variables)
    for i, path in enumerate(files):
        name = os.path.basename(path)
        marker = ">" if i == current_index else " "
        print(f"{marker} {i+1:03d}. {name}")

    print("-" * 60)
    print("Commands: play | pause | stop | next | prev | v N | v+ | v- | m | pl | exit")


# ---------------------------
# Main control loop
# ---------------------------

def main_loop(player, instance, files, folder, find_files_fn, clamp_fn, start_index=0):
    """
    Main loop that controls playback and handles user commands.
    All external needs are passed in as parameters:
      - player, instance: vlc objects
      - files: list of file paths
      - folder: path used by 'pl' reload command
      - find_files_fn: function to reload playlist (signature: folder -> list)
      - clamp_fn: function to wrap indices (signature: index, n -> index)
    This keeps the function independent from module-level state.
    """
    current = clamp_fn(start_index, len(files))

    while True:
        # Announce current track (local variables only)
        print(f"\nNow playing [{current+1}/{len(files)}]: {os.path.basename(files[current])}")
        try:
            play_track(player, instance, files[current])
        except Exception as e:
            print("Failed to start playback:", e)

        # Inner loop: commands for this track
        while True:
            show_ui(player, files, current)

            try:
                cmd = input("\nEnter command: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                try:
                    player.stop()
                except Exception:
                    pass
                return

            # PLAY
            if cmd in ("play", "p"):
                try:
                    player.play()
                except Exception:
                    pass
                time.sleep(0.1)

            # PAUSE
            elif cmd == "pause":
                try:
                    player.pause()
                except Exception:
                    pass
                time.sleep(0.1)

            # STOP
            elif cmd in ("stop", "s"):
                try:
                    player.stop()
                except Exception:
                    pass
                time.sleep(0.05)

            # VOLUME show
            elif cmd == "volume":
                try:
                    print("Volume:", player.audio_get_volume())
                except Exception:
                    print("Volume: ?")

            # V+ / V- quick changes
            elif cmd == "v+":
                try:
                    cur = player.audio_get_volume() or 0
                    new = min(100, cur + 10)
                    player.audio_set_volume(new)
                    print("Volume set to", new)
                except Exception:
                    pass

            elif cmd == "v-":
                try:
                    cur = player.audio_get_volume() or 0
                    new = max(0, cur - 10)
                    player.audio_set_volume(new)
                    print("Volume set to", new)
                except Exception:
                    pass

            # Set volume exactly: "v 50" or "v 75"
            elif cmd.startswith("v "):
                parts = cmd.split()
                if len(parts) >= 2:
                    try:
                        val = int(parts[1])
                        val = max(0, min(100, val))
                        player.audio_set_volume(val)
                        print("Volume set to", val)
                    except Exception:
                        print("Invalid volume value. Use: v 50")
                else:
                    print("Use: v 50")

            # MUTE toggle
            elif cmd == "m":
                try:
                    cur = player.audio_get_mute()
                    player.audio_set_mute(not cur)
                    print("Muted." if not cur else "Unmuted.")
                except Exception:
                    print("Mute toggle failed.")

            # NEXT track
            elif cmd in ("next", "n"):
                try:
                    player.stop()
                except Exception:
                    pass
                current = clamp_fn(current + 1, len(files))
                break  # start new track

            # PREVIOUS track
            elif cmd in ("prev", "b", "back"):
                try:
                    player.stop()
                except Exception:
                    pass
                current = clamp_fn(current - 1, len(files))
                break  # start new track

            # RELOAD playlist from folder and show it
            elif cmd == "pl":
                try:
                    new_files = find_files_fn(folder)
                    # update the existing list in-place so references remain valid
                    files[:] = new_files
                    print_playlist(files, current)
                except Exception as e:
                    print("Failed to reload playlist:", e)
                # remain in inner loop

            # EXIT
            elif cmd in ("exit", "quit"):
                print("Goodbye.")
                try:
                    player.stop()
                except Exception:
                    pass
                return

            # Unknown command
            else:
                print("Unknown command. Try: play, pause, next, prev, v 50, m, pl, exit")


# ---------------------------
# Program entry (wiring)
# ---------------------------

def main(argv):
    """
    Program entry. This is the only place that creates configuration and wires
    dependencies together. All other functions remain independent and parameter-driven.
    """
    # Local configuration values (only here)
    allowed_ext = (".mp3", ".wav", ".flac", ".ogg", ".mp4")
    start_index = 0

    # Resolve folder using a pure function that receives argv
    folder = get_media_folder_from_args(argv)

    # Load playlist (raise and handle errors locally)
    try:
        files = find_media_files(folder, allowed_ext)
    except ValueError as e:
        print(e)
        print("Create the folder and put media files there, or run:")
        print("  python MF_Player_ALPHA.py /path/to/folder")
        sys.exit(1)

    # Show playlist before starting
    print_playlist(files, start_index)

    # Create vlc objects (pure function that returns them)
    inst, player = create_vlc_player()

    # Run main loop; pass functions that main_loop needs so it doesn't read globals
    try:
        main_loop(
            player=player,
            instance=inst,
            files=files,
            folder=folder,
            find_files_fn=lambda f: find_media_files(f, allowed_ext),
            clamp_fn=clamp_index,
            start_index=start_index,
        )
    finally:
        # Ensure we stop playback on exit
        try:
            player.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main(sys.argv)
