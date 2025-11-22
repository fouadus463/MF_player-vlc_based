#!/usr/bin/env python3
"""
MF_Player: Simple terminal media player using python-vlc.
Features:
- Play audio/video
- Pause/Resume
- Stop
- Next/Previous track
- Repeat toggle (automatic repeat if on)
Save as MF_Player.py
"""

import os
import sys
import time
import threading

try:
    import vlc
except ImportError:
    print("Error: python-vlc is not installed. Install it with 'pip install python-vlc'.")
    sys.exit(1)

# ------------------------------
# Playlist and Player Management
# ------------------------------
class MFPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.playlist = []
        self.index = 0
        self.repeat = False
        self.lock = threading.Lock()
        self.running = True

    def add_to_playlist(self, path):
        if os.path.exists(path):
            self.playlist.append(path)
        else:
            print(f"File not found: {path}")

    def play(self, index=None):
        with self.lock:
            if index is not None:
                self.index = index
            if not self.playlist:
                print("Playlist is empty.")
                return
            media = self.instance.media_new(self.playlist[self.index])
            self.player.set_media(media)
            self.player.play()
            print(f"Now playing: {self.playlist[self.index]}")

    def stop(self):
        with self.lock:
            self.player.stop()

    def pause(self):
        with self.lock:
            self.player.pause()

    def next_track(self):
        with self.lock:
            self.index = (self.index + 1) % len(self.playlist)
            self.play(self.index)

    def prev_track(self):
        with self.lock:
            self.index = (self.index - 1) % len(self.playlist)
            self.play(self.index)

    def toggle_repeat(self):
        self.repeat = not self.repeat
        print(f"Repeat is now {'ON' if self.repeat else 'OFF'}")

    # Monitor track end and auto-repeat
    def monitor(self):
        while self.running:
            time.sleep(1)
            if self.player.get_state() == vlc.State.Ended:
                if self.repeat:
                    print("Repeating track...")
                    self.play(self.index)
                else:
                    self.next_track()


# ------------------------------
# CLI Interface
# ------------------------------
def print_help():
    print("""
Commands:
  play [n]   - Play track number n (0-based index)
  pause      - Pause/Resume
  stop       - Stop
  next       - Next track
  prev       - Previous track
  repeat     - Toggle repeat mode
  add PATH   - Add file to playlist
  list       - Show playlist
  help       - Show this help
  quit       - Exit player
""")

def main():
    player = MFPlayer()

    # Start monitoring thread
    monitor_thread = threading.Thread(target=player.monitor, daemon=True)
    monitor_thread.start()

    print("MF_Player started. Type 'help' for commands.")

    while True:
        try:
            cmd = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            player.running = False
            player.stop()
            break

        if not cmd:
            continue

        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()

        if action == "play":
            if len(parts) == 2 and parts[1].isdigit():
                idx = int(parts[1])
                player.play(idx)
            else:
                player.play()
        elif action == "pause":
            player.pause()
        elif action == "stop":
            player.stop()
        elif action == "next":
            player.next_track()
        elif action == "prev":
            player.prev_track()
        elif action == "repeat":
            player.toggle_repeat()
        elif action == "add":
            if len(parts) == 2:
                player.add_to_playlist(parts[1])
            else:
                print("Usage: add PATH")
        elif action == "list":
            if not player.playlist:
                print("Playlist empty.")
            else:
                for i, t in enumerate(player.playlist):
                    print(f"{i}: {t}")
        elif action == "help":
            print_help()
        elif action == "quit":
            print("Exiting...")
            player.running = False
            player.stop()
            break
        else:
            print("Unknown command. Type 'help' for commands.")


if __name__ == "__main__":
    main()
