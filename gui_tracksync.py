import tkinter as tk
from tkinter import filedialog, messagebox,Toplevel  # For file dialog and message popups
import os
import threading  # To keep the GUI responsive while running tasks

def select_folder(entry):
    """
    Opens a file dialog for the user to select a folder and updates the corresponding entry widget.
    """
    folder = filedialog.askdirectory()  # Opens a directory chooser dialog
    if folder:
        entry.delete(0, tk.END)  # Clear any existing text in the entry widget
        entry.insert(0, folder)  # Insert the selected folder path into the entry

def start_process(script_mode, priority_entry, secondary_entry, output_entry, status_label):
    """
    Initiates the track merging process based on the selected mode (Preserve or Clean).
    Runs the process in a separate thread to avoid freezing the GUI.
    """
    # Fetch paths and the output folder name from the GUI fields
    priority_folder = priority_entry.get().strip()
    secondary_folder = secondary_entry.get().strip()
    output_folder_name = output_entry.get().strip()

    # Validate user input
    if not priority_folder or not secondary_folder or not output_folder_name:
        messagebox.showwarning("Input Error", "Please fill in all fields.")  # Alert if any input is missing
        return

    # Build the output folder path
    output_folder = os.path.join(os.path.dirname(priority_folder), output_folder_name)

    # Update the status label to indicate processing has started
    status_label.config(text="Processing...", fg="blue")

    # Run the process in a separate thread to keep the GUI responsive
    threading.Thread(
        target=run_tracksync,
        args=(script_mode, priority_folder, secondary_folder, output_folder, status_label),
    ).start()

def run_tracksync(script_mode, priority_folder, secondary_folder, output_folder, status_label):
    """
    Runs the core functionality of TrackSync based on the selected mode.
    Imports the appropriate script (tracksync or tracksyncclean) dynamically.
    """
    try:
        # Dynamically import the appropriate script based on the selected mode
        if script_mode == "Preserve Numbering":
            from tracksync import load_files_with_metadata, match_tracks, renumber_and_copy_files
        else:
            from tracksyncclean import load_files_with_metadata, match_tracks, renumber_and_copy_files

        # Process files from the priority folder
        print("Loading priority folder...")
        priority_files = load_files_with_metadata(priority_folder)

        # Process files from the secondary folder
        print("Loading secondary folder...")
        secondary_files = load_files_with_metadata(secondary_folder)

        # Match tracks between folders and combine them
        print("Matching tracks and preserving priority order...")
        final_list = match_tracks(priority_files, secondary_files)

        # Renumber and copy files into the output folder
        print("Renumbering and copying files to output folder...")
        renumber_and_copy_files(final_list, output_folder)

        # Update status and notify the user upon success
        status_label.config(text="Process completed successfully!", fg="green")
        messagebox.showinfo("Success", "Tracks merged and saved successfully!")
    except Exception as e:
        # Handle and display any errors encountered during the process
        status_label.config(text="Error occurred!", fg="red")
        messagebox.showerror("Error", str(e))

def show_help():
    """
    Displays a simple, crystal-clear help message with an option to read more.
    """
    # Create a new top-level window for the help message
    help_window = Toplevel()
    help_window.title("Help")
    help_window.geometry("400x200")
    help_window.resizable(False, False)  # Disable resizing

    # Simple explanation text
    help_text = (
        "Preserve Numbering:\n"
        "  - Keeps the numbers already in the song names.\n"
        "  - Example: '002. Song Title.mp3' → 'Track 001 - 002. Song Title.mp3'\n\n"
        "Clean Numbering:\n"
        "  - Removes the old numbers from the song names.\n"
        "  - Example: '002. Song Title.mp3' → 'Track 001 - Song Title.mp3'\n\n"
    )

    # Add the explanation text
    label = tk.Label(help_window, text=help_text, justify="left", wraplength=380)
    label.pack(pady=10, padx=10)

    # Add a "Read More" button
    read_more_button = tk.Button(help_window, text="Read More", command=show_detailed_explanation)
    read_more_button.pack(pady=5)

    # Add a "Close" button
    close_button = tk.Button(help_window, text="Close", command=help_window.destroy)
    close_button.pack(pady=5)


def show_detailed_explanation():
    """
    Opens a new window with a more detailed explanation of the modes.
    """
    # Create a new window for the detailed explanation
    detail_window = Toplevel()
    detail_window.title("Detailed Explanation")
    detail_window.geometry("500x400")
    detail_window.resizable(False, False)  # Disable resizing

    # Detailed explanation text
    detailed_text = (
        "Detailed Explanation:\n\n"
        "Preserve Numbering:\n"
        "This option keeps the original numbering in your file names. "
        "For example, if you have downloaded songs using ByClick Downloader "
        "or similar tools, the numbers in the filenames (e.g., '002.') might indicate "
        "the original order of the tracks. By choosing this option, these numbers will "
        "remain part of the final filenames, alongside the new track numbering.\n\n"
        "Clean Numbering:\n"
        "This option removes the original numbering from the filenames to give them "
        "a cleaner appearance. This is especially useful if the old numbering is inconsistent "
        "or redundant, and you want your files to follow a uniform format like 'Track 001 - Song Title'.\n\n"
        "Why This Feature Exists:\n"
        "I designed this feature to solve an issue I initially experienced with ByClick Downloader. "
        "Specifically, if you downloaded files with 'Add track numbers to file names'. enabled, "
        "the downloaded files were assigned track numbers based on the playlist order. "
        "However, these numbers could become misaligned when videos were removed or made private "
        "(essentially unavailable) from the playlist. This feature gives users the flexibility to either "
        "keep those original numbers, preserving their context, or remove them for a cleaner, standardized format."
    )
    # Add the detailed explanation text
    label = tk.Label(detail_window, text=detailed_text, justify="left", wraplength=480)
    label.pack(pady=10, padx=10)

    # Add a "Close" button
    close_button = tk.Button(detail_window, text="Close", command=detail_window.destroy)
    close_button.pack(pady=10)
def create_gui():
    """
    Sets up the graphical user interface (GUI) for the TrackSync tool.
    """
    root = tk.Tk()
    root.title("TrackSync - Playlist Merger")
    root.geometry("800x400")

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=2)
    root.grid_columnconfigure(2, weight=1)

    tk.Label(root, text="Priority Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    priority_entry = tk.Entry(root)
    priority_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    tk.Button(root, text="Browse", command=lambda: select_folder(priority_entry)).grid(row=0, column=2, padx=10, pady=10, sticky="e")

    tk.Label(root, text="Secondary Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    secondary_entry = tk.Entry(root)
    secondary_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
    tk.Button(root, text="Browse", command=lambda: select_folder(secondary_entry)).grid(row=1, column=2, padx=10, pady=10, sticky="e")

    tk.Label(root, text="Output Folder Name:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    output_entry = tk.Entry(root)
    output_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    tk.Label(root, text="Mode:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    mode_var = tk.StringVar(value="Preserve Numbering")
    tk.Radiobutton(root, text="Preserve Numbering", variable=mode_var, value="Preserve Numbering").grid(row=3, column=1, sticky="w")
    tk.Radiobutton(root, text="Clean Numbering", variable=mode_var, value="Clean Numbering").grid(row=3, column=1, sticky="e")
    tk.Button(root, text="?", command=show_help, width=2).grid(row=3, column=2, padx=5, pady=10, sticky="w")

    status_label = tk.Label(root, text="", fg="blue")
    status_label.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

    tk.Button(
        root,
        text="Run",
        command=lambda: start_process(mode_var.get(), priority_entry, secondary_entry, output_entry, status_label),
    ).grid(row=4, column=1, pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()