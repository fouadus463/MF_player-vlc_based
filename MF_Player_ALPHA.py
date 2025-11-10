import os
import sys
import time

try:
    import vlc
except Exception:
    print("MP_Player can't find or load vlc")
    print("install vlc via terminal")
    print("install python-vlc via PIP")
    raise

def media_files(media_folder: str | None = None, allowed: tuple | None = None) -> list:
    if allowed is None:
        allowed = (".mp3", ".wav", ".flac", ".ogg", ".mp4")
    if not media_folder:
        if len(sys.argv) > 1:
            media_folder = sys.argv[1]
        else:
            media_folder = os.path.join(os.getcwd(), "audio")
    if not os.path.isdir(media_folder):
        print("Folder not found:", media_folder)
        print("Create the folder and put media files there, or run:")
        print("    python player.py /your/folder")
        return []
    media_list = []
    for entry in sorted(os.listdir(media_folder)):
        fullpath = os.path.join(media_folder, entry)
        if os.path.isfile(fullpath) and entry.lower().endswith(tuple(ext.lower() for ext in allowed)):
            media_list.append(fullpath)
    try:
        refresh.ui()
    except NameError:
        pass
    return media_list

class MF_Player:
    def __init__(self, media_path):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = self.instance.media_new(media_path)
        self.player.set_media(self.media)
        self.status = "stopped"

    def refresh_ui(self):
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
        print("======================================")
        print("🎵 MF MEDIA PLAYER")
        print("======================================")
        print("commands : play | pause | stop | quit")
        print("======================================")
    
    def play(self):
        self.player.play()
        self.status = "playing"
        self.refresh_ui()

    def pause(self):
        self.player.pause()
        self.status = "paused"
        self.refresh_ui()

    def stop(self):
        self.player.stop()
        self.status = "stopped"
        self.refresh_ui()

def main():
    files = media_files()
    if files:
        path = files[0]
    else:
        path = "song.mp3"
    player = MF_Player(path)
    player.refresh_ui()
    try:
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "play":
                player.play()
            elif cmd == "pause":
                player.pause()
            elif cmd == "stop":
                player.stop()
            elif cmd == "quit":
                player.stop()
                break
            else:
                print("Unknown command")
    except KeyboardInterrupt:
        player.stop()

if __name__ == "__main__":
    main()
