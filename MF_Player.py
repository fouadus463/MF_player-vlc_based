import os  # Operating system interface for file/directory operations
import sys  # System-specific parameters and functions (for command-line arguments)
import time  # Time access and conversions (for sleep delays)
import threading  # Thread-based parallelism (imported but not used in this code)

try:
    import vlc  # Python bindings for VLC media player
except Exception as e:  # Catch any import errors
    print("MP_Player can't find or load vlc ")  # Error message
    print("Please Try to FIX it by")  # Help instructions
    print("install vlc via terminal")  # Installation step 1
    print("install python-vlc via PIP")  # Installation step 2
    raise  # Re-raise the exception to stop execution

# Check if user provided a folder path as command-line argument
if len(sys.argv) > 1:  # If there's at least one argument after the script name
    media_folder = sys.argv[1]  # Use the provided path
else:
    media_folder = os.path.join(os.getcwd(), "audio")  # Default to "audio" folder in current directory

# Define allowed file extensions for media files
allowed = (".mp3", ".wav", ".flac", ".ogg", ".mp4")  # Tuple of supported formats

# Verify the media folder exists
if not os.path.isdir(media_folder):  # Check if path is not a directory
    print("Folder not found", media_folder)  # Error message
    print("Create the folder and put media files there, or run python : python player.py /your/folder")  # Help
    sys.exit(1)  # Exit with error code 1

# Collect all media files from the folder
files = []  # Initialize empty list for file paths
for name in os.listdir(media_folder):  # Iterate through all items in folder
    full = os.path.join(media_folder, name)  # Create full path by joining folder and filename
    if not os.path.isfile(full):  # Skip if item is not a file (e.g., subdirectories)
        continue  # Move to next iteration
    if full.lower().endswith(allowed):  # Check if file extension matches allowed formats (case-insensitive)
        files.append(full)  # Add file path to list

files.sort()  # Sort files alphabetically for consistent ordering

# Check if any media files were found
if not files:  # If list is empty
    print("No media files found in:", media_folder)  # Error message
    print("Supported extensions:", allowed)  # Show supported formats
    sys.exit(1)  # Exit with error code 1

# Display the playlist to user
print("Playlist:")  # Header
for i, f in enumerate(files, 1):  # Enumerate with 1-based indexing
    print(f" {i}. {os.path.basename(f)}")  # Print index and filename only (not full path)

# Initialize VLC player
instance = vlc.Instance()  # Create VLC instance
player = instance.media_player_new()  # Create a new media player object

current_index = 0  # Track which song is currently selected (0-based index)
is_running = True  # Flag to control the main loop

# Main playback loop
while is_running:  # Continue until user exits
    # Load and start playing the current track
    print(f"\nNow playing [{current_index + 1}/{len(files)}]: {os.path.basename(files[current_index])}")  # Show current track
    media_file = instance.media_new(files[current_index])  # Create media object from file path
    player.set_media(media_file)  # Load media into player
    player.play()  # Start playback
    time.sleep(0.5)  # Brief delay to allow player to initialize

    # Command loop for user interaction
    while True:  # Inner loop for commands during playback
        print("\n--- Commands ---")  # Menu header
        print("p : play")  # Play/resume command
        print("pause : pause/resume")  # Toggle pause
        print("s : stop")  # Stop playback
        print("n : next")  # Skip to next track
        print("b : back/previous")  # Go to previous track
        print("exit : exit")  # Quit program
        print("v+ : increase volume")
        print("v- : decrease volume")
        print("m : mute/unmute")
        choose = input("Enter command: ").strip().lower()  # Get user input, remove whitespace, convert to lowercase

        # FIXED: Proper conditional checks (original code had "or 'p'" which always evaluated to True)
        if choose == "p" or choose == "play":  # Check if input matches play commands
            print("Playing...")  # Confirmation message
            player.play()  # Resume/start playback
            time.sleep(0.5)  # Brief delay for feedback

        elif choose == "pause":  # Check for pause command
            print("Paused/Resumed.")  # Confirmation (VLC pause toggles)
            player.pause()  # Toggle pause state
            time.sleep(0.5)  # Brief delay for feedback

        elif choose == "s" or choose == "stop":  # Check if input matches stop commands
            print("Stopping...")  # Confirmation message
            player.stop()  # Stop playback
            time.sleep(0.5)  # Brief delay

        elif choose == "volume":
            print(f"current volume : {player.get_volume()}")
        elif choose == "v+":
            current_volume = player.audio_get_volume()
            new_volume = min(100, current_volume +10)
            player.audio_set_volume(new_volume)
            print(f"volume increased to:{new_volume}")
        elif choose == "v-":
            current_volume = player.audio_get_volume()
            new_volume = max(0, current_volume -10)
            player.audio_set_volume(new_volume)
            print(f"volume increased to:{new_volume}")
        elif choose.startswith("v "):
            try:
                volume = int(choose[2:])
                volume = max(0, min(100, volume))
                player.audio_set_volume(volume)
                print(f"volume set to {volume}%")
            except ValueError:
                print("Invalid volume value. use v 50")
        elif choose == "m" or choose == "mute":
            if player.audio_get_mute():
                player.audii_get_mute(False)
                print("audio is unmuted...)
            elif: 
                player.audio_get_mute()
                player.audio_set_mute(True)
                print("audio is muted")
elif choose == "m":
            if player.audio_get_mute():
                player.audio_set_mute(false)
                print("Unmuted.")
            else:
                player.audio_get_mute()
                player.audio_set_mute(true)
                print("Muted.")

        elif choose == "n" or choose == "next":  # Check for next command
            print("Next track...")  # Confirmation message
            player.stop()  # Stop current playback
            current_index += 1  # Increment track index
            if current_index >= len(files):  # Check if we've reached the end of playlist
                current_index = 0  # Wrap around to first track
            break  # Exit command loop to load new track

        elif choose == "b" or choose == "back" or choose == "previous":  # Check for previous command
            print("Previous track...")  # Confirmation message
            player.stop()  # Stop current playback
            current_index -= 1  # Decrement track index
            if current_index < 0:  # Check if we've gone before the first track
                current_index = len(files) - 1  # Wrap around to last track
            break  # Exit command loop to load new track

        elif choose == "exit" or choose == "quit":  # Check for exit commands
            print("Goodbye!")  # Farewell message
            player.stop()  # Stop playback
            is_running = False  # Set flag to exit main loop
            break  # Exit command loop

        else:  # If input doesn't match any command
            print("I don't understand that command.")  # Error message
            # Loop continues, allowing user to try again

# Cleanup (optional, Python handles this automatically)
# player.release()  # Release player resources
# instance.release()  # Release VLC instanceN
