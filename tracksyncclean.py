import os
import shutil
from mutagen import File
from mutagen.id3 import ID3NoHeaderError
from difflib import SequenceMatcher
import unicodedata
import re

def load_files_with_metadata(folder):
    valid_extensions = (".mp3", ".flac", ".wav", ".m4a")
    files_with_metadata = []
    index = 0

    for filename in os.listdir(folder):
        if not filename.lower().endswith(valid_extensions):
            continue

        filepath = os.path.join(folder, filename)

        try:
            audio = File(filepath, easy=True)
            if audio is None:
                print(f"Warning: Unable to read metadata for {filename}")
                continue

            title = audio.get("title", ["Unknown Title"])[0]
            artist = audio.get("artist", ["Unknown Artist"])[0]
            track_num_str = audio.get("tracknumber", ["0"])[0]
            track_num_str = track_num_str.split("/")[0]

            try:
                track_num_val = int(track_num_str)
            except ValueError:
                track_num_val = 0

            files_with_metadata.append({
                "folder_index": index,
                "track_num": track_num_val,
                "filename": filename,
                "folder": folder,
                "title": title,
                "artist": artist
            })
            index += 1

        except ID3NoHeaderError:
            print(f"Warning: {filename} has no ID3 header.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    return files_with_metadata

def match_tracks(priority_files, secondary_files):
    used_secondary = set()
    matched_priority = []

    # Attempt to match priority tracks to secondary ones
    for p in priority_files:
        for s_index, s in enumerate(secondary_files):
            if s_index in used_secondary:
                continue

            title_similarity = SequenceMatcher(None, p["title"].lower(), s["title"].lower()).ratio()
            artist_similarity = SequenceMatcher(None, p["artist"].lower(), s["artist"].lower()).ratio()

            # Adjust thresholds as you like
            if title_similarity > 0.9 or (title_similarity > 0.75 and artist_similarity > 0.75):
                used_secondary.add(s_index)
                break
        matched_priority.append(p)

    unmatched_secondary = [s for s_index, s in enumerate(secondary_files) if s_index not in used_secondary]

    # Sort each list by original folder order
    matched_priority_sorted = sorted(matched_priority, key=lambda x: x["folder_index"])
    unmatched_secondary_sorted = sorted(unmatched_secondary, key=lambda x: x["folder_index"])

    return matched_priority_sorted + unmatched_secondary_sorted

def renumber_and_copy_files(final_list, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    track_counter = 1
    for item in final_list:
        filename = item["filename"]
        source_folder = item["folder"]

        src_path = os.path.join(source_folder, filename)

        # 1) Remove leading track numbers like "002." or "010 -"
        cleaned_original = remove_leading_track_number(filename)

        # 2) Sanitize and build new filename
        new_filename = f"Track {track_counter:03d} - {sanitize_filename(cleaned_original)}"
        track_counter += 1

        dest_path = os.path.join(output_folder, new_filename)
        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied: {filename} -> {new_filename}")
        except Exception as e:
            print(f"Error copying {filename}: {e}")

def remove_leading_track_number(name):
    """
    Removes leading digits (and optional punctuation/spaces) from the start of the filename.
    Examples:
        "002. MySong.mp3"  -> "MySong.mp3"
        "010 - Another.mp3" -> "Another.mp3"
        "10  Some Song.mp3" -> "Some Song.mp3"
    """
    # Regex: ^\d+ means one or more digits at the start
    #        [\s\.\-_]* means optional space, dot, dash, or underscore
    # Use strip() at the end to remove leftover whitespace
    return re.sub(r'^\d+[\s\.\-_]*', '', name).strip()

def sanitize_filename(name):
    name = unicodedata.normalize("NFKD", name)
    return re.sub(r'[\\/:*?"<>|]', "_", name)

if __name__ == "__main__":
    priority_folder = os.path.normpath(input("Enter the path to the priority folder: ").strip('"'))
    secondary_folder = os.path.normpath(input("Enter the path to the secondary folder: ").strip('"'))
    output_folder_name = input("Enter the output folder name: ").strip('"')

    output_folder = os.path.join(os.path.dirname(priority_folder), output_folder_name)

    print("Loading priority folder...")
    priority_files = load_files_with_metadata(priority_folder)

    print("Loading secondary folder...")
    secondary_files = load_files_with_metadata(secondary_folder)

    print("Matching tracks and preserving priority order...")
    final_list = match_tracks(priority_files, secondary_files)

    print("Renumbering and copying files to output folder...")
    renumber_and_copy_files(final_list, output_folder)

    print("Process completed successfully!")
