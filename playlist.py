# mf_player/playlist.py
"""Discover media files and small playlist utilities."""
import os

def find_media_files(folder, allowed_ext):
    if not os.path.isdir(folder):
        raise FileNotFoundError(folder)
    files = []
    for name in os.listdir(folder):
        full = os.path.join(folder, name)
        if os.path.isfile(full) and full.lower().endswith(allowed_ext):
            files.append(full)
    files.sort()
    return files

def clamp_index(index, n):
    if n <= 0:
        return 0
    return index % n
