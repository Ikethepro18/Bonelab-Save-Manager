import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sys
import pathlib
import shutil
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def get_save_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def get_active_save_game():
    settings_path = os.path.expanduser(os.path.join('~', 'AppData', 'LocalLow', 'Stress Level Zero', 'BONELAB', 'settings.json'))
    try:
        with open(settings_path, 'r') as file:
            settings_data = json.load(file)
            active_save_game = settings_data.get('active_save_game')
            return active_save_game
    except (IOError, ValueError):
        messagebox.showerror("Error", "Failed to retrieve active save game.")
        return None

def update_active_save_game(active_save_game):
    settings_path = os.path.expanduser(os.path.join('~', 'AppData', 'LocalLow', 'Stress Level Zero', 'BONELAB', 'settings.json'))
    try:
        with open(settings_path, 'r') as file:
            settings_data = json.load(file)
            settings_data['active_save_game'] = active_save_game
        with open(settings_path, 'w') as file:
            json.dump(settings_data, file, indent=4)
    except (IOError, ValueError):
        messagebox.showerror("Error", "Failed to update active save game.")

def save_button_clicked():
    selected_item = listbox.get(listbox.curselection())
    if not selected_item.endswith(".json"):
        messagebox.showerror("Error", "Invalid save file selected.")
    else:
        update_active_save_game(selected_item)
        active_save_label.config(text="Active Save: " + selected_item)
        messagebox.showinfo("Success", "Active save game updated successfully.")

def add_save_button_clicked():
    file_path = filedialog.askopenfilename(initialdir=saves_folder, title="Select .json file to save", filetypes=[("JSON Files", "*.json")])
    if file_path:
        file_name = os.path.basename(file_path)
        new_file_path = os.path.join(saves_folder, file_name)
        shutil.move(file_path, new_file_path)
        listbox.insert(tk.END, get_save_name(new_file_path) + ".json")
        messagebox.showinfo("Success", "Save file added successfully.")

def rename_save_button_clicked():
    selected_item = listbox.get(listbox.curselection())
    if not selected_item.endswith(".json"):
        messagebox.showerror("Error", "Invalid save file selected.")
    else:
        new_save_name = simpledialog.askstring("Rename Save", "Enter a new name for the save (without spaces):")
        if new_save_name and " " not in new_save_name:
            new_file_name = new_save_name + ".json"
            selected_index = listbox.curselection()
            listbox.delete(selected_index)
            old_file_path = os.path.join(saves_folder, selected_item)
            new_file_path = os.path.join(saves_folder, new_file_name)
            os.rename(old_file_path, new_file_path)
            listbox.insert(selected_index, new_save_name + ".json")
            messagebox.showinfo("Success", "Save file renamed successfully.")
        else:
            messagebox.showerror("Error", "Invalid save name. Please enter a name without spaces.")

def delete_save_button_clicked():
    selected_item = listbox.get(listbox.curselection())
    if not selected_item.endswith(".json"):
        messagebox.showerror("Error", "Invalid save file selected.")
    else:
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete the save file?")
        if confirmation:
            file_path = os.path.join(saves_folder, selected_item)
            os.remove(file_path)
            listbox.delete(tk.ACTIVE)
            messagebox.showinfo("Success", "Save file deleted successfully.")

def open_folder_button_clicked():
    subprocess.Popen('explorer "' + saves_folder + '"')

def refresh_save_list():
    listbox.delete(0, tk.END)
    save_files = [file for file in os.listdir(saves_folder) if file.endswith(".json") and file != "BL_ArenaPlayer_01.json"]
    if not save_files:
        no_saves_label = tk.Label(window, text="No .json files found.")
        no_saves_label.pack(pady=10)
    else:
        for file in save_files:
            file_path = os.path.join(saves_folder, file)
            listbox.insert(tk.END, get_save_name(file_path) + ".json")

class SavesChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        refresh_save_list()

def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = pathlib.Path(sys._MEIPASS)
    else:
        base_path = pathlib.Path(__file__).resolve().parent
    return str(base_path / relative_path)

window = tk.Tk()
window.title("Bonelab Save Manager")

icon_path = get_resource_path("icon.ico")
window.iconbitmap(icon_path)

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = (screen_width - 352) // 2
y = (screen_height - 300) // 2

window.geometry(f"352x300+{x}+{y}")

listbox = tk.Listbox(window)
listbox.pack(fill=tk.BOTH, expand=True)

saves_folder = os.path.expanduser(os.path.join('~', 'AppData', 'LocalLow', 'Stress Level Zero', 'BONELAB', 'Saves'))
refresh_save_list()

active_save_game = get_active_save_game()
if active_save_game:
    active_save_label = tk.Label(window, text="Active Save: " + active_save_game)
    active_save_label.pack(pady=5)

button_frame = tk.Frame(window)
button_frame.pack(pady=5)

save_button = tk.Button(button_frame, text="Set Active Save", command=save_button_clicked)
save_button.pack(side="left", padx=5)

add_save_button = tk.Button(button_frame, text="Add Save", command=add_save_button_clicked)
add_save_button.pack(side="left", padx=5)

rename_save_button = tk.Button(button_frame, text="Rename Save", command=rename_save_button_clicked)
rename_save_button.pack(side="left", padx=5)

delete_save_button = tk.Button(button_frame, text="Delete Save", command=delete_save_button_clicked)
delete_save_button.pack(side="left", padx=5)

open_folder_button = tk.Button(window, text="Open Saves Folder", command=open_folder_button_clicked)
open_folder_button.pack(pady=5)

event_handler = SavesChangeHandler()
observer = Observer()
observer.schedule(event_handler, path=saves_folder, recursive=False)
observer.start()

window.mainloop()
