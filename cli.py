# mf_player/cli.py
"""Entry point and wiring. Keeps main() as the only place that reads argv."""
import sys
import time
from .playlist import find_media_files, clamp_index
from .player import create_player, play_track
from .player import pause, stop as player_stop
from .player import set_volume as player_set_volume
from .player import get_time, get_length, get_state
from .player import audio_get_volume, audio_get_mute, audio_set_mute
from .ui import show_ui, print_playlist
from .util import safe_get_volume, safe_set_volume, safe_stop

ALLOWED_EXT = (".mp3", ".wav", ".flac", ".ogg", ".mp4", ".m4a")

def get_media_folder_from_args(argv):
    return argv[1] if len(argv) > 1 else "audio"

def main(argv):
    folder = get_media_folder_from_args(argv)
    try:
        files = find_media_files(folder, ALLOWED_EXT)
    except Exception as e:
        print(e)
        print("Create the folder and put media files there, or run:")
        print("  python -m mf_player.cli /path/to/folder")
        sys.exit(1)

    if not files:
        print("No media files found in", folder)
        sys.exit(1)

    print_playlist(files, 0)

    try:
        inst, player = create_player()
    except Exception as e:
        print('Failed to create VLC player:', e)
        sys.exit(1)

    current = clamp_index(0, len(files))

    while True:
        print(f"\nNow playing [{current+1}/{len(files)}]: {files[current]}")
        try:
            play_track(player, inst, files[current])
        except Exception as e:
            print('Play failed:', e)

        while True:
            show_ui(player, files, current)
            try:
                cmd = input('\nEnter command: ').strip().lower()
            except (KeyboardInterrupt, EOFError):
                print('\nExiting.')
                safe_stop(player)
                return

            if cmd in ('play', 'p'):
                try:
                    player.play()
                except Exception:
                    pass

            elif cmd == 'pause':
                try:
                    pause(player)
                except Exception:
                    pass

            elif cmd in ('stop', 's'):
                safe_stop(player)
                print('Stopped.')

            elif cmd in ('volume', 'vol'):
                print('Volume:', safe_get_volume(player))

            elif cmd == 'v+':
                cur = safe_get_volume(player)
                new = min(100, cur + 10)
                setv = safe_set_volume(player, new)
                print('Volume set to', setv if setv is not None else 'failed')

            elif cmd == 'v-':
                cur = safe_get_volume(player)
                new = max(0, cur - 10)
                setv = safe_set_volume(player, new)
                print('Volume set to', setv if setv is not None else 'failed')

            elif cmd.startswith('v '):
                parts = cmd.split()
                if len(parts) >= 2:
                    try:
                        val = int(parts[1])
                        val = max(0, min(100, val))
                        setv = safe_set_volume(player, val)
                        print('Volume set to', setv if setv is not None else 'failed')
                    except Exception:
                        print('Invalid volume value. Use: v 50')
                else:
                    print('Use: v 50')

            elif cmd in ('m', 'mute'):
                try:
                    # toggle
                    audio_set_mute(player, not bool(audio_get_mute(player)))
                    time.sleep(0.06)
                    print('Muted.' if audio_get_mute(player) else 'Unmuted.')
                except Exception:
                    print('Mute toggle failed.')

            elif cmd in ('next', 'n'):
                safe_stop(player)
                current = clamp_index(current + 1, len(files))
                break

            elif cmd in ('prev', 'b', 'back'):
                safe_stop(player)
                current = clamp_index(current - 1, len(files))
                break

            elif cmd == 'pl':
                try:
                    files = find_media_files(folder, ALLOWED_EXT)
                    print_playlist(files, current)
                except Exception as e:
                    print('Failed to reload playlist:', e)

            elif cmd in ('exit', 'quit'):
                safe_stop(player)
                print('Goodbye.')
                return

            else:
                print('Unknown command. Try: play, pause, next, prev, v 50, v+, v-, m, pl, exit')

if __name__ == '__main__':
    main(sys.argv)
