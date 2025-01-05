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

    # We’ll keep an index counter to preserve the order they appear in folder
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

            # Safely retrieve tags
            title = audio.get("title", ["Unknown Title"])[0]
            artist = audio.get("artist", ["Unknown Artist"])[0]
            track_num_str = audio.get("tracknumber", ["0"])[0]
            track_num_str = track_num_str.split("/")[0]  # if tracknumber is something like "5/10"

            try:
                track_num_val = int(track_num_str)
            except ValueError:
                track_num_val = 0

            # Store everything in a tuple or dict, plus an index to preserve folder order
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
    """
    1) Preserve all priority_files exactly in order.
    2) Attempt to match them to secondary_files based on high title/artist similarity.
    3) Exclude matched secondary_files from being duplicated.
    4) Add unmatched secondary_files at the end in the order they appear in the secondary folder.
    """

    used_secondary = set()  # store indices of secondary files already matched
    matched_priority = []

    # Step 1: For each priority track, see if there's a close match in secondary.
    #         We'll skip adding the secondary track if matched (no duplicates).
    for p in priority_files:
        # By default, the priority track is "unmatched" in the sense that we keep it
        # but let's see if there's a close match in secondary folder
        for s_index, s in enumerate(secondary_files):
            # Already used?
            if s_index in used_secondary:
                continue

            # Compare similarity
            title_similarity = SequenceMatcher(None, p["title"].lower(), s["title"].lower()).ratio()
            artist_similarity = SequenceMatcher(None, p["artist"].lower(), s["artist"].lower()).ratio()

            # You can tweak the thresholds. Using a combined approach:
            # If title_similarity is very high, or both title and artist are moderately high, consider matched.
            if title_similarity > 0.9 or (title_similarity > 0.75 and artist_similarity > 0.75):
                # Mark the secondary file as used
                used_secondary.add(s_index)
                break

        # Add the priority track into final list regardless, in original order
        matched_priority.append(p)

    # Step 2: Add unmatched secondary files to the final list
    unmatched_secondary = []
    for s_index, s in enumerate(secondary_files):
        if s_index not in used_secondary:
            unmatched_secondary.append(s)

    # Sort priority by folder_index to preserve folder 1's original sequence
    matched_priority_sorted = sorted(matched_priority, key=lambda x: x["folder_index"])

    # Sort unmatched secondary by folder_index (the order they appear in folder 2)
    unmatched_secondary_sorted = sorted(unmatched_secondary, key=lambda x: x["folder_index"])

    # Combine them: priority first, then unmatched secondary
    combined = matched_priority_sorted + unmatched_secondary_sorted

    # Return in a list, so we can reassign track numbers in a single pass
    return combined


def renumber_and_copy_files(final_list, output_folder):
    """
    Assign new track numbers in the order they appear in final_list.
    Copy them to output_folder with sanitized filenames, preserving metadata.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    track_counter = 1
    for item in final_list:
        filename = item["filename"]
        source_folder = item["folder"]

        src_path = os.path.join(source_folder, filename)

        # Format: Track 001 - original_filename
        new_filename = f"Track {track_counter:03d} - {sanitize_filename(filename)}"
        track_counter += 1

        dest_path = os.path.join(output_folder, new_filename)

        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied: {filename} -> {new_filename}")
        except Exception as e:
            print(f"Error copying {filename}: {e}")


def sanitize_filename(name):
    # If using "NFKD" breaks certain Chinese characters, switch to "NFC".
    name = unicodedata.normalize("NFKD", name)
    # Replace illegal file characters
    return re.sub(r'[\\/:*?"<>|]', "_", name)


if __name__ == "__main__":
    # priority_folder = os.path.normpath(input("Enter the path to the priority folder: ").strip('"'))
    # secondary_folder = os.path.normpath(input("Enter the path to the secondary folder: ").strip('"'))
    # output_folder_name = input("Enter the output folder name: ").strip('"')

    priority_folder = os.path.normpath(input("Enter the path to the priority folder: ").strip('"'))
    secondary_folder = os.path.normpath(input("Enter the path to the secondary folder: ").strip('"'))
    output_folder_name = input("Enter the output folder name: ").strip('"')

    # output folder is in the same directory as priority folder
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
