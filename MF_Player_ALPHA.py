#!/usr/bin/env python3
"""
Simple terminal media player using python-vlc.
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
    print("Commands: play | pause | stop | next | prev | v N | v+ | v- | m | exit")


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
#!/usr/bin/env python3
"""
MF_Player_ONEFILE.py — Single-file media player (CLI) with repeat support.

Features:
- Play / pause / stop
- Next / previous
- Playlist management (in-memory)
- Repeat toggle (repeats current track when ON)
- Shuffle (basic)
- Status display
- Uses python-vlc (libVLC). Install: pip install python-vlc

Note: This file intentionally contains clearly separated sections (marked)
that correspond to your previous multi-file layout (cli, player, playlist, ui, util),
but everything lives in one file per your preference.
"""

import vlc
import threading
import time
import sys
import os
import random
from typing import List, Optional

# ============================
# util.py (utility helpers)
# ============================
def human_time(ms: int) -> str:
    """Convert milliseconds to mm:ss (simple)."""
    if ms < 0:
        return "0:00"
    s = ms // 1000
    m = s // 60
    s = s % 60
    return f"{m}:{s:02d}"

def is_audio_file(path: str) -> bool:
    """Basic check — extend if desired."""
    ext = os.path.splitext(path)[1].lower()
    return ext in (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg")

# ============================
# playlist.py (playlist manager)
# ============================
class Playlist:
    """
    Simple playlist manager.
    Stores list of file paths and manages current index.
    """
    def __init__(self, items: Optional[List[str]] = None):
        self.items: List[str] = items[:] if items else []
        self.index: int = 0

    def add(self, path: str):
        self.items.append(path)

    def remove(self, idx: int):
        if 0 <= idx < len(self.items):
            del self.items[idx]
            # clamp index
            if self.index >= len(self.items):
                self.index = max(0, len(self.items)-1)

    def current(self) -> Optional[str]:
        if not self.items:
            return None
        return self.items[self.index]

    def next(self) -> Optional[str]:
        if not self.items:
            return None
        self.index = (self.index + 1) % len(self.items)
        return self.current()

    def prev(self) -> Optional[str]:
        if not self.items:
            return None
        self.index = (self.index - 1) % len(self.items)
        return self.current()

    def jump(self, idx: int) -> Optional[str]:
        if 0 <= idx < len(self.items):
            self.index = idx
            return self.current()
        return None

    def shuffle(self):
        if not self.items:
            return
        cur = self.current()
        random.shuffle(self.items)
        # try to keep the same current song if possible
        if cur in self.items:
            self.index = self.items.index(cur)
        else:
            self.index = 0

    def clear(self):
        self.items = []
        self.index = 0

    def list_items(self) -> List[str]:
        return self.items[:]

# ============================
# player.py (VLC wrapper + event handling)
# ============================
class MFPlayerCore:
    """
    Core playback logic using python-vlc.
    Handles repeat toggle, end-of-track behavior, play/pause, and playlist transitions.
    """
    def __init__(self, playlist: Playlist):
        self.instance = vlc.Instance()
        self.vlc_player = self.instance.media_player_new()
        self.playlist = playlist

        # Control flags
        self.repeat = False       # When True, repeat the current track (loop single track)
        self.lock = threading.Lock()

        # Event manager to detect end of media
        em = self.vlc_player.event_manager()
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end)

        # A small thread to optionally update status (non-blocking)
        self._status_thread = threading.Thread(target=self._status_loop, daemon=True)
        self._status_running = False

    # --------------------
    # Internal helpers
    # --------------------
    def _set_media_by_path(self, path: str):
        """Assign a media file to the VLC player (no auto-play)."""
        media = self.instance.media_new_path(path)
        self.vlc_player.set_media(media)

    def _on_end(self, event):
        """
        Called by libVLC when media ends.
        Behavior:
          - If repeat ON -> restart same track
          - Else -> advance to next track (if any) and play it
        Note: Use lock to read flags safely since events run in VLC threads.
        """
        with self.lock:
            do_repeat = self.repeat

        if do_repeat:
            # Restart the same media
            try:
                # Some libVLC versions need stop/play; set_time(0) also helps
                self.vlc_player.stop()
                self.vlc_player.play()
                self.vlc_player.set_time(0)
            except Exception:
                # Defensive fallback: reassign media then play
                cur = self.playlist.current()
                if cur:
                    self._set_media_by_path(cur)
                    self.vlc_player.play()
        else:
            # Advance to next track and play if exists
            nxt = self.playlist.next()
            if nxt:
                self._set_media_by_path(nxt)
                self.vlc_player.play()
            else:
                # nothing to play
                self.vlc_player.stop()

    def _status_loop(self):
        """Optional status updater (prints small status every second while playing)."""
        self._status_running = True
        while self._status_running:
            time.sleep(1)
            # If you want periodic UI updates, put them here.
            # We don't print automatically to avoid spamming when using the CLI.
        self._status_running = False

    # --------------------
    # Public controls
    # --------------------
    def play_current(self) -> bool:
        """Play the current playlist item. Return True if started."""
        cur = self.playlist.current()
        if not cur:
            return False
        self._set_media_by_path(cur)
        self.vlc_player.play()
        return True

    def play(self):
        """Resume or play current."""
        state = self.vlc_player.get_state()
        if state in (vlc.State.Playing,):
            return
        # If no media loaded, load current
        if not self.vlc_player.get_media():
            self.play_current()
            return
        self.vlc_player.play()

    def pause(self):
        self.vlc_player.pause()

    def stop(self):
        self.vlc_player.stop()

    def next(self):
        nxt = self.playlist.next()
        if nxt:
            self._set_media_by_path(nxt)
            self.vlc_player.play()
            return True
        return False

    def prev(self):
        p = self.playlist.prev()
        if p:
            self._set_media_by_path(p)
            self.vlc_player.play()
            return True
        return False

    def toggle_repeat(self) -> bool:
        """Toggle repeat state (thread-safe). Returns new state."""
        with self.lock:
            self.repeat = not self.repeat
            return self.repeat

    def set_repeat(self, val: bool):
        with self.lock:
            self.repeat = bool(val)

    def get_status(self) -> dict:
        """Return basic status info for UI display."""
        cur = self.playlist.current()
        state = str(self.vlc_player.get_state())
        pos_ms = -1
        length_ms = -1
        try:
            pos_ms = self.vlc_player.get_time()
            length_ms = self.vlc_player.get_length()
        except Exception:
            pass
        return {
            "state": state,
            "current": cur,
            "position_ms": pos_ms,
            "length_ms": length_ms,
            "repeat": self.repeat,
            "playlist_len": len(self.playlist.items),
            "index": self.playlist.index,
        }

# ============================
# ui.py / cli.py (command interface)
# ============================
def print_help():
    print("Commands:")
    print("  play             : play / resume")
    print("  pause            : pause")
    print("  stop             : stop")
    print("  next             : next track")
    print("  prev             : previous track")
    print("  repeat           : toggle repeat (repeat single track ON/OFF)")
    print("  repeat on|off    : set repeat explicitly")
    print("  shuffle          : shuffle playlist")
    print("  add <path>       : add file to playlist")
    print("  del <index>      : delete item index (0-based)")
    print("  jump <index>     : jump to index and play")
    print("  list             : list playlist items")
    print("  status           : show current status")
    print("  quit             : exit program")
    print("  help             : this message")

def cli_loop(core: MFPlayerCore, playlist: Playlist):
    """
    Minimal REPL for controlling the player.
    All input parsing and UI lives here to keep core playback separate.
    """
    print("MF_Player (one-file). Type 'help' for commands.")
    while True:
        try:
            cmdline = input("mf> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            core.stop()
            break

        if not cmdline:
            continue

        parts = cmdline.split()
        cmd = parts[0].lower()

        if cmd == "help":
            print_help()

        elif cmd == "play":
            started = core.play()
            # play() is idempotent; if nothing loaded try play_current
            if not core.vlc_player.get_media():
                if not core.play_current():
                    print("Playlist empty. Use 'add <path>' to add files.")

        elif cmd == "pause":
            core.pause()
            print("Paused.")

        elif cmd == "stop":
            core.stop()
            print("Stopped.")

        elif cmd == "next":
            if core.next():
                print("Next track playing.")
            else:
                print("No next track.")

        elif cmd == "prev":
            if core.prev():
                print("Previous track playing.")
            else:
                print("No previous track.")

        elif cmd == "repeat":
            # support "repeat on/off" too
            if len(parts) >= 2:
                arg = parts[1].lower()
                if arg in ("on", "1", "true"):
                    core.set_repeat(True)
                elif arg in ("off", "0", "false"):
                    core.set_repeat(False)
                print("Repeat is", "ON" if core.repeat else "OFF")
            else:
                new_state = core.toggle_repeat()
                print("Repeat toggled ->", "ON" if new_state else "OFF")

        elif cmd == "shuffle":
            playlist.shuffle()
            print("Playlist shuffled.")

        elif cmd == "add":
            if len(parts) < 2:
                print("Usage: add <path>")
                continue
            path = " ".join(parts[1:])
            if not os.path.exists(path):
                print("File does not exist:", path)
                continue
            playlist.add(path)
            print("Added:", path)

        elif cmd in ("del", "remove"):
            if len(parts) < 2:
                print("Usage: del <index>")
                continue
            try:
                idx = int(parts[1])
                playlist.remove(idx)
                print("Removed index", idx)
            except Exception as e:
                print("Invalid index:", e)

        elif cmd == "jump":
            if len(parts) < 2:
                print("Usage: jump <index>")
                continue
            try:
                idx = int(parts[1])
                if playlist.jump(idx):
                    core._set_media_by_path(playlist.current())
                    core.play()
                    print("Jumped to", idx)
                else:
                    print("Invalid index.")
            except ValueError:
                print("Index must be integer.")

        elif cmd == "list":
            items = playlist.list_items()
            if not items:
                print("[playlist empty]")
            else:
                for i, it in enumerate(items):
                    marker = ">" if i == playlist.index else " "
                    print(f"{marker} [{i}] {it}")

        elif cmd == "status":
            s = core.get_status()
            print("State:", s["state"])
            print("Repeat:", "ON" if s["repeat"] else "OFF")
            print("Track index:", s["index"], "of", s["playlist_len"])
            print("Current:", s["current"])
            print("Position:", human_time(s["position_ms"]), "/", human_time(s["length_ms"]))

        elif cmd == "quit":
            core.stop()
            print("Goodbye.")
            break

        else:
            print("Unknown command. Type 'help'.")


# ============================
# main (entry point) - acts like cli.py main
# ============================
def main():
    # If user passes files on command line, pre-load them into playlist
    initial_files = []
    if len(sys.argv) > 1:
        # treat all arguments as files
        for p in sys.argv[1:]:
            if os.path.exists(p):
                initial_files.append(p)
            else:
                print("Warning: file not found:", p)

    playlist = Playlist(initial_files)
    core = MFPlayerCore(playlist)

    # If playlist not empty, start playing first track automatically
    if playlist.items:
        print("Auto-playing first track.")
        core.play_current()
    else:
        print("Playlist empty. Use 'add <path>' to add files or pass files as arguments.")

    cli_loop(core, playlist)

if __name__ == "__main__":
    main()
