import os
import sys
import time

try:
    import vlc
except Exception as e:
    print("MP_Player can't find or load vlc")
    print("Please Try to FIX it by")
    print("install vlc via terminal")
    print("install python-vlc via PIP")
    raise

ALLOWED = (".mp3", ".wav", ".flac", ".ogg", ".mp4")


def get_media_folder():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.join(os.getcwd(), "audio")


def collect_files(media_folder, allowed=ALLOWED):
    if not os.path.isdir(media_folder):
        print("Folder not found", media_folder)
        print("Create the folder and put media files there, or run python : python player.py /your/folder")
        sys.exit(1)
    result = []
    for name in os.listdir(media_folder):
        full = os.path.join(media_folder, name)
        if not os.path.isfile(full):
            continue
        if full.lower().endswith(allowed):
            result.append(full)
    result.sort()
    if not result:
        print("No media files found in:", media_folder)
        print("Supported extensions:", allowed)
        sys.exit(1)
    return result


def print_playlist(files):
    print("Playlist:")
    for i, f in enumerate(files, 1):
        print(f" {i}. {os.path.basename(f)}")


def init_player():
    instance = vlc.Instance()
    player = instance.media_player_new()
    return instance, player


def set_track(player, instance, path):
    media = instance.media_new(path)
    player.set_media(media)
    player.play()
    time.sleep(0.5)


def clamp_index(index, length):
    if length == 0:
        return 0
    return index % length


def change_volume_by(player, delta):
    try:
        current = player.audio_get_volume()
        if current is None or current < 0:
            current = 0
    except Exception:
        current = 0
    new = max(0, min(100, current + delta))
    player.audio_set_volume(new)
    print(f"volume set to: {new}")


def set_volume(player, value):
    value = max(0, min(100, value))
    player.audio_set_volume(value)
    print(f"volume set to {value}%")


def toggle_mute(player):
    muted = player.audio_get_mute()
    player.audio_set_mute(not muted)
    print("Muted." if not muted else "Unmuted.")


def command_loop(player, instance, files, start_index=0):
    current_index = clamp_index(start_index, len(files))
    running = True
    while running:
        print(f"\nNow playing [{current_index + 1}/{len(files)}]: {os.path.basename(files[current_index])}")
        set_track(player, instance, files[current_index])

        while True:
            print("\n--- Commands ---")
            print("p : play")
            print("pause : pause/resume")
            print("s : stop")
            print("n : next")
            print("b : back/previous")
            print("exit : exit")
            print("volume : show current volume")
            print("v+ : increase volume")
            print("v- : decrease volume")
            print("v N : set volume to N (0-100) e.g. v 50")
            print("m : mute/unmute")
            try:
                choose = input("Enter command: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                player.stop()
                return

            if choose in ("p", "play"):
                player.play()
                time.sleep(0.2)

            elif choose == "pause":
                player.pause()
                time.sleep(0.2)

            elif choose in ("s", "stop"):
                player.stop()
                time.sleep(0.1)

            elif choose in ("volume",):
                try:
                    v = player.audio_get_volume()
                except Exception:
                    v = 0
                print(f"current volume : {v}")

            elif choose == "v+":
                change_volume_by(player, 10)

            elif choose == "v-":
                change_volume_by(player, -10)

            elif choose.startswith("v "):
                parts = choose.split()
                if len(parts) >= 2:
                    try:
                        vol = int(parts[1])
                        set_volume(player, vol)
                    except ValueError:
                        print("Invalid volume value. use v 50")
                else:
                    print("Invalid command. use v 50")

            elif choose == "m":
                toggle_mute(player)

            elif choose in ("n", "next"):
                player.stop()
                current_index = clamp_index(current_index + 1, len(files))
                break

            elif choose in ("b", "back", "previous"):
                player.stop()
                current_index = clamp_index(current_index - 1, len(files))
                break

            elif choose in ("exit", "quit"):
                print("Goodbye!")
                player.stop()
                running = False
                break

            else:
                print("I don't understand that command.")


def main():
    media_folder = get_media_folder()
    files = collect_files(media_folder)
    print_playlist(files)
    instance, player = init_player()
    try:
        command_loop(player, instance, files, start_index=0)
    finally:
        try:
            player.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
