#!/usr/bin/env python3
"""
Simple terminal media player using python-vlc.

- Very linear and beginner-friendly.
- Clear blocks: setup -> playlist -> main loop -> command handling.
- Keep it simple: only basic commands, easy to understand.
"""

import os
import sys
import time

# Try to import vlc; if it fails, give a clear message and stop.
try:
    import vlc
except Exception:
    print("MF_Player can't find or load python-vlc (libVLC).")
    print("Install system VLC and python-vlc, e.g.:")
    print("  sudo apt install vlc")
    print("  pip install python-vlc")
    sys.exit(1)


# ---------------------------
# Configuration / Constants
# ---------------------------
ALLOWED_EXT = (".mp3", ".wav", ".flac", ".ogg", ".mp4")


# ---------------------------
# Small utility helpers
# ---------------------------

def human_time(ms):
    """Convert milliseconds to MM:SS (simple). Return '--:--' if unknown."""
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

def get_media_folder_from_args():
    """Get media folder from argv or default to ./audio."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.join(os.getcwd(), "audio")


def find_media_files(folder):
    """
    Return sorted list of media file paths.
    Exits the program with a message if folder missing or empty.
    """
    if not os.path.isdir(folder):
        print("Folder not found:", folder)
        print("Create it and put media files there, or run:")
        print("  python simple_player.py /path/to/folder")
        sys.exit(1)

    files = []
    for name in os.listdir(folder):
        full = os.path.join(folder, name)
        if os.path.isfile(full) and full.lower().endswith(ALLOWED_EXT):
            files.append(full)

    files.sort()
    if not files:
        print("No media files found in:", folder)
        print("Supported extensions:", ALLOWED_EXT)
        sys.exit(1)
    return files


def print_playlist(files, current_index=0):
    """Show the playlist with the current track marked with '>'."""
    print("Playlist:")
    for i, path in enumerate(files):
        marker = ">" if i == current_index else " "
        print(f" {marker} {i+1:03d}. {os.path.basename(path)}")


# ---------------------------
# Player helpers (simple)
# ---------------------------

def create_vlc_player():
    """Create and return a vlc instance and player."""
    inst = vlc.Instance()
    player = inst.media_player_new()
    return inst, player


def play_track(player, instance, path):
    """Load the path into the player and start playback."""
    media = instance.media_new(path)
    player.set_media(media)
    player.play()
    # small sleep helps VLC start and give reliable get_time/get_length calls
    time.sleep(0.3)


def clamp_index(index, n):
    """Wrap index into [0, n-1] using modulo. If n==0 return 0."""
    if n <= 0:
        return 0
    return index % n


# ---------------------------
# Simple display for the user
# ---------------------------

def show_ui(player, files, current_index):
    """
    Clear screen and show:
      - current state, time, volume
      - short playlist with marker on current
      - short help line
    """
    clear_screen()
    # try reading some values; keep things simple and tolerant of errors
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

    print(f"State: {state}   Track: {current_index + 1}/{len(files)}")
    print(f"Time : {human_time(pos)} / {human_time(length)}")
    print(f"Volume: {vol}")
    print("-" * 60)

    # playlist: show all (for beginners it's simpler to see whole list)
    for i, path in enumerate(files):
        name = os.path.basename(path)
        marker = ">" if i == current_index else " "
        print(f"{marker} {i+1:03d}. {name}")

    print("-" * 60)
    print("Commands: play | pause | stop | next | prev | v N | v+ | v- | m | pl | exit")


# ---------------------------
# Command loop (main)
# ---------------------------

def main_loop(player, instance, files, folder, start_index=0):
    """
    Very linear main loop:
      - set current index
      - play the track
      - inside inner loop: show UI, read user input, handle commands
      - when user selects next/prev we break to outer loop and start new track
    """
    current = clamp_index(start_index, len(files))

    running = True
    while running:
        # Announce and start playing the current track
        print(f"\nNow playing [{current+1}/{len(files)}]: {os.path.basename(files[current])}")
        play_track(player, instance, files[current])

        # Inner loop: handle commands while this track is active
        while True:
            # Refresh UI so user sees updated time/volume
            show_ui(player, files, current)

            # Show short command prompt
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

            # PAUSE / RESUME
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
                current = clamp_index(current + 1, len(files))
                break  # break inner loop -> start new track in outer loop

            # PREVIOUS track
            elif cmd in ("prev", "b", "back"):
                try:
                    player.stop()
                except Exception:
                    pass
                current = clamp_index(current - 1, len(files))
                break

            # RELOAD playlist from folder and show it
            elif cmd == "pl":
                try:
                    new_files = find_media_files(folder)
                    files[:] = new_files   # update list in-place
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
# Program entry
# ---------------------------

def main():
    folder = get_media_folder_from_args()
    files = find_media_files(folder)
    print_playlist(files, 0)

    inst, player = create_vlc_player()

    try:
        main_loop(player, inst, files, folder, start_index=0)
    finally:
        # Ensure we stop playback on exit
        try:
            player.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
