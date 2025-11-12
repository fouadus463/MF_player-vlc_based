#!/usr/bin/env python3
import os
import sys
import time

try:
    import vlc
except Exception:
    print("MF_Player can't find or load vlc")
    print("Please try to fix it by:")
    print(" - install VLC (system package)")
    print(" - install python-vlc via pip")
    raise

ALLOWED = (".mp3", ".wav", ".flac", ".ogg", ".mp4")  # supported extensions


def get_media_folder():
    # return folder from argv or default "audio" in cwd
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.join(os.getcwd(), "audio")


def collect_files(media_folder, allowed=ALLOWED):
    # gather and return sorted media file paths
    if not os.path.isdir(media_folder):
        print("Folder not found", media_folder)
        print("Create the folder and put media files there, or run:")
        print("  python player.py /your/folder")
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
    # print playlist names only
    print("Playlist:")
    for i, f in enumerate(files, 1):
        print(f" {i}. {os.path.basename(f)}")


def init_player():
    # create and return VLC instance and player
    instance = vlc.Instance()
    player = instance.media_player_new()
    return instance, player


def set_track(player, instance, path):
    # load a file into the player and start playback
    try:
        media = instance.media_new(path)
        player.set_media(media)
        player.play()
        time.sleep(0.5)
    except Exception as e:
        print("Error loading track:", e)


def clamp_index(index, length):
    # wrap index around playlist using modulo
    if length <= 0:
        return 0
    return index % length


def change_volume_by(player, delta):
    # change volume by delta and clamp 0-100
    try:
        current = player.audio_get_volume()
        if current is None or current < 0:
            current = 0
    except Exception:
        current = 0
    new = max(0, min(100, current + delta))
    try:
        player.audio_set_volume(new)
    except Exception:
        pass
    print(f"volume set to: {new}")


def ms_to_mmss(ms):
    if not ms or ms <= 0:
        return "00:00"
    m, s = divmod(ms // 1000, 60)
    return f"{m:02d}:{s:02d}"


def clear_screen():
    # cross-platform clear
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def refresh_display(player, files, current_index):
    clear_screen()
    # header / status
    try:
        state = str(player.get_state())
    except Exception:
        state = "UNKNOWN"

    try:
        length_ms = player.get_length()
        position_ms = player.get_time()
    except Exception:
        length_ms = -1
        position_ms = -1

    try:
        volume = player.audio_get_volume()
    except Exception:
        volume = "?"

    try:
        muted = player.audio_get_mute()
    except Exception:
        muted = False

    print(f"state: {state}  Track: {current_index + 1}/{len(files)}")
    print(f"time: {ms_to_mmss(position_ms)} / {ms_to_mmss(length_ms)}")
    print(f"volume: {volume}  muted: {muted}")
    print("_" * 60)

    # playlist (compact; mark current track with >)
    for i, path in enumerate(files):
        name = os.path.basename(path)
        marker = ">" if i == current_index else " "
        print(f"{marker} {i+1:03d}. {name}")

    print("_" * 60)
    print("Command: play/pause, stop, next, prev, v <0-100>, mute, seek <sec>, quit")


def set_volume(player, value):
    # set exact volume value 0-100
    value = max(0, min(100, value))
    try:
        player.audio_set_volume(value)
    except Exception:
        pass
    print(f"volume set to {value}%")


def toggle_mute(player):
    # toggle mute state
    try:
        muted = player.audio_get_mute()
    except Exception:
        muted = False
    new_state = not muted
    try:
        player.audio_set_mute(new_state)
    except Exception:
        pass
    print("Muted." if new_state else "Unmuted.")


def command_loop(player, instance, files, media_folder, start_index=0, refresh_ui=None):
    # main loop: plays tracks and handles user commands
    current_index = clamp_index(start_index, len(files))
    running = True
    while running:
        print(f"\nNow playing [{current_index + 1}/{len(files)}]: {os.path.basename(files[current_index])}")
        set_track(player, instance, files[current_index])

        while True:
            # refresh UI if provided (call before input so CLI can update)
            if callable(refresh_ui):
                try:
                    refresh_ui(player, files, current_index)
                except Exception:
                    pass

            # command menu
            print("\n--- Commands ---")
            print("p : play")
            print("pause : pause/resume")
            print("s : stop")
            print("n : next")
            print("b : back/previous")
            print("pl : show playlist (reloads folder)")
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
                try:
                    player.stop()
                except Exception:
                    pass
                return

            if choose in ("p", "play"):
                try:
                    player.play()
                except Exception:
                    pass
                time.sleep(0.2)

            elif choose == "pause":
                try:
                    player.pause()
                except Exception:
                    pass
                time.sleep(0.2)

            elif choose in ("s", "stop"):
                try:
                    player.stop()
                except Exception:
                    pass
                time.sleep(0.1)

            elif choose == "volume":
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
                try:
                    player.stop()
                except Exception:
                    pass
                current_index = clamp_index(current_index + 1, len(files))
                break

            elif choose in ("b", "back", "previous"):
                try:
                    player.stop()
                except Exception:
                    pass
                current_index = clamp_index(current_index - 1, len(files))
                break

            elif choose == "pl":
                # reload playlist from the same media folder
                try:
                    new_files = collect_files(media_folder)
                    files[:] = new_files  # update in-place so outer reference stays valid
                    print_playlist(files)
                except Exception as e:
                    print("Error reloading playlist:", e)
                # don't change current_index here; let user choose next action
                continue

            elif choose in ("exit", "quit"):
                print("Goodbye!")
                try:
                    player.stop()
                except Exception:
                    pass
                running = False
                break

            else:
                print("I don't understand that command.")


def main():
    # program entry: gather files, init player and start command loop
    media_folder = get_media_folder()
    files = collect_files(media_folder)
    print_playlist(files)
    instance, player = init_player()
    try:
        command_loop(player, instance, files, media_folder, start_index=0, refresh_ui=refresh_display)
    finally:
        try:
            player.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
