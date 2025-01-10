import tkinter as tk
from tkinter import filedialog, messagebox  # For file dialog and message popups
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
    Displays a help message explaining the modes.
    """
    help_text = (
        "Preserve Numbering:\n"
        "  - Keeps the numbers already in the song names.\n"
        "  - Example: '002. Song Title.mp3' → 'Track 001 - 002. Song Title.mp3'\n\n"
        "Clean Numbering:\n"
        "  - Removes the old numbers from the song names.\n"
        "  - Example: '002. Song Title.mp3' → 'Track 001 - Song Title.mp3'"

    )
    messagebox.showinfo("Help - Modes", help_text)

def create_gui():
    """
    Sets up the graphical user interface (GUI) for the TrackSync tool.
    """
    root = tk.Tk()  # Create the main application window
    root.title("TrackSync - Playlist Merger")  # Set the window title
    root.geometry("800x400")  # Set the initial window size

    # Configure the grid to make the widgets responsive
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=2)
    root.grid_columnconfigure(2, weight=1)

    # Priority folder input
    tk.Label(root, text="Priority Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    priority_entry = tk.Entry(root)
    priority_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")  # Expand horizontally
    tk.Button(root, text="Browse", command=lambda: select_folder(priority_entry)).grid(row=0, column=2, padx=10, pady=10, sticky="e")

    # Secondary folder input
    tk.Label(root, text="Secondary Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    secondary_entry = tk.Entry(root)
    secondary_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
    tk.Button(root, text="Browse", command=lambda: select_folder(secondary_entry)).grid(row=1, column=2, padx=10, pady=10, sticky="e")

    # Output folder name input
    tk.Label(root, text="Output Folder Name:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    output_entry = tk.Entry(root)
    output_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    # Mode selection with help button
    tk.Label(root, text="Mode:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    mode_var = tk.StringVar(value="Preserve Numbering")  # Default mode
    tk.Radiobutton(root, text="Preserve Numbering", variable=mode_var, value="Preserve Numbering").grid(row=3, column=1, sticky="w")
    tk.Radiobutton(root, text="Clean Numbering", variable=mode_var, value="Clean Numbering").grid(row=3, column=1, sticky="e")
    tk.Button(root, text="?", command=show_help, width=2).grid(row=3, column=2, padx=5, pady=10, sticky="w")  # Help button

    # Status Label
    status_label = tk.Label(root, text="", fg="blue")
    status_label.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

    # Run Button
    tk.Button(
        root,
        text="Run",
        command=lambda: start_process(mode_var.get(), priority_entry, secondary_entry, output_entry, status_label),
    ).grid(row=4, column=1, pady=20)

    root.mainloop()  # Start the Tkinter event loop


if __name__ == "__main__":
    create_gui()
