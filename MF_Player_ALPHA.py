import os
import time

try:
    import vlc  # Python bindings for VLC media player
except Exception as e:  # Catch any import errors
    print("MP_Player can't find or load vlc ")  # Error message
    print("Please Try to FIX it by")  # Help instructions
    print("install vlc via terminal")  # Installation step 1
    print("install python-vlc via PIP")  # Installation step 2
    raise  # Re-raise the exception to stop execution

# Place this after your imports:
# import os, sys
# and make sure a refresh object with method ui() exists in your program (or replace refresh.ui() with your UI refresh function).

def media_files(media_folder: str | None = None, allowed: tuple | None = None) -> list:
    """
    Collect media files from a folder and refresh the UI.

    Args:
        media_folder: optional path string. If None:
            - uses sys.argv[1] if provided, otherwise defaults to ./audio
        allowed: optional tuple of allowed extensions (eg. ('.mp3', '.wav')). If None, defaults to common types.

    Returns:
        list of full paths to media files found in the folder (sorted).
    """
    # --- Defaults ---
    if allowed is None:
        allowed = (".mp3", ".wav", ".flac", ".ogg", ".mp4")  # supported formats

    # If caller didn't provide a folder, check command-line args, else default to ./audio
    if not media_folder:  # empty or None
        if len(sys.argv) > 1:
            media_folder = sys.argv[1]
        else:
            media_folder = os.path.join(os.getcwd(), "audio")

    # Verify the folder exists
    if not os.path.isdir(media_folder):
        print("Folder not found:", media_folder)
        print("Create the folder and put media files there, or run:")
        print("    python player.py /your/folder")
        # return empty list instead of exiting — easier for calling code to handle
        return []

    # Walk the folder and collect files with allowed extensions
    media_list = []
    for entry in sorted(os.listdir(media_folder)):  # sorted for predictable order
        fullpath = os.path.join(media_folder, entry)
        # Only add regular files with allowed extension (case-insensitive)
        if os.path.isfile(fullpath) and entry.lower().endswith(tuple(ext.lower() for ext in allowed)):
            media_list.append(fullpath)

    # Call UI refresh so the CLI (or GUI) updates its view of available media.
    # NOTE: make sure a 'refresh' object with method ui() exists in your program,
    # or replace the line below with the correct function to refresh your UI.
    try:
        refresh.ui()
    except NameError:
        # If refresh isn't defined, just ignore (prevents crash). Optionally print a warning.
        # Remove this except block if you prefer the program to fail loudly.
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
        os.system("clear") #clear the terminal
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
        player = CliPlayer("song.mp3") #this line must be recoded to changer the path to audio
        player.refresh_ui()
        while True:
            cmd  = input("> ").strip().lower()
            if cmd == "play":
                player.play()
            elif cmd == "pause":
                player.pause()
            elif cmd == "stop":
                player.stop()
            elif cmd == "quit":
                break
            else:
                print("Unknown command")

    if __name__ == "__main__":
        main()