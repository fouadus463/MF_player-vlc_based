# 🎧 CLI Media Player — Functions Explained

Each section below shows the **function**, followed by a **simple explanation**  
of what it does and what each parameter means.

---

## 🧩 `collect_files()`

```python
import os

def collect_files(media_folder: str, allowed: tuple | None = None) -> list:
    files = []
    for name in os.listdir(media_folder):
        full = os.path.join(media_folder, name)
        if not os.path.isfile(full):
            continue
        if allowed and not full.lower().endswith(allowed):
            continue
        files.append(full)
    return files
Explanation:
Collects all files inside a folder that match allowed extensions.

Parameters:

media_folder — path of the folder that contains media.

allowed — file types you want (like (".mp3", ".mp4")).
If None, all files are accepted.

Example:

python
Copy code
songs = collect_files("/home/user/Music", (".mp3", ".wav"))
⚙️ init()
python
Copy code
import vlc

def init(vlc_instance: vlc.Instance) -> vlc.MediaPlayer:
    player = vlc_instance.media_player_new()
    return player
Explanation:
Creates a new VLC player that can play, pause, or stop media.

Parameters:

vlc_instance — the main VLC engine object.

Example:

python
Copy code
vlc_instance = vlc.Instance()
player = init(vlc_instance)
📂 media_files()
python
Copy code
def media_files(media_folder: str | None = None, allowed: tuple | None = None) -> list:
    if not media_folder:
        media_folder = "./media"
    return collect_files(media_folder, allowed)
Explanation:
Gets a list of playable files from a folder (default ./media).

Parameters:

media_folder — path to folder with media.

allowed — file extensions to include.

Example:

python
Copy code
files = media_files("/home/user/Videos", (".mp4", ".mkv"))
▶️ play_media()
python
Copy code
def play_media(player, file_path: str) -> None:
    media = vlc.Media(file_path)
    player.set_media(media)
    player.play()
Explanation:
Loads and starts playing a media file.

Parameters:

player — VLC player created by init().

file_path — the full path of the file to play.

Example:

python
Copy code
play_media(player, "/home/user/Music/song.mp3")
⏸️ pause_media()
python
Copy code
def pause_media(player) -> None:
    player.pause()
Explanation:
Pauses or resumes playback.

Parameters:

player — VLC player instance currently playing media.

Example:

python
Copy code
pause_media(player)
⏹️ stop_media()
python
Copy code
def stop_media(player) -> None:
    player.stop()
Explanation:
Stops playback completely and resets position to start.

Parameters:

player — VLC player object.

Example:

python
Copy code
stop_media(player)
🔁 next_media()
python
Copy code
def next_media(player, files: list, index: int) -> int:
    index = (index + 1) % len(files)
    play_media(player, files[index])
    return index
Explanation:
Plays the next media file in the list.

Parameters:

player — VLC player instance.

files — list of all media paths.

index — the current file number in the list.

Example:

python
Copy code
index = next_media(player, files, index)
🔄 previous_media()
python
Copy code
def previous_media(player, files: list, index: int) -> int:
    index = (index - 1) % len(files)
    play_media(player, files[index])
    return index
Explanation:
Plays the previous file in the list.

Parameters:

player — VLC player instance.

files — list of all media paths.

index — the current file number in the list.

Example:

python
Copy code
index = previous_media(player, files, index)
⏱️ seek_media()
python
Copy code
def seek_media(player, seconds: int) -> None:
    current = player.get_time()
    player.set_time(current + (seconds * 1000))
Explanation:
Moves playback forward or backward by a given number of seconds.

Parameters:

player — VLC player instance.

seconds — time to skip (positive = forward, negative = back).

Example:

python
Copy code
seek_media(player, 10)   # Forward 10 sec
seek_media(player, -5)   # Backward 5 sec
🔈 set_volume()
python
Copy code
def set_volume(player, volume: int) -> None:
    player.audio_set_volume(volume)
Explanation:
Changes the playback volume.

Parameters:

player — VLC player instance.

volume — sound level (0 to 100).

Example:

python
Copy code
set_volume(player, 80)
💾 save_settings()
python
Copy code
import json

def save_settings(settings_path: str, settings: dict) -> None:
    with open(settings_path, "w") as f:
        json.dump(settings, f)
Explanation:
Saves player settings (volume, last song, etc.) into a JSON file.

Parameters:

settings_path — where to save settings file.

settings — what data to save (dictionary).

Example:

python
Copy code
save_settings("config.json", {"volume": 70})
📖 load_settings()
python
Copy code
import json
import os

def load_settings(settings_path: str) -> dict:
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            return json.load(f)
    return {}
Explanation:
Loads saved settings if the file exists, or returns empty data.

Parameters:

settings_path — path to settings JSON file.

Example:

python
Copy code
settings = load_settings("config.json")
✅ Tip:
When you add new functions, use this same format:
1️⃣ Write the function,
2️⃣ Explain it clearly,
3️⃣ Focus on what each parameter means,
4️⃣ Add a small example.