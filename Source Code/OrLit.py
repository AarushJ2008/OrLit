# File: OrLit.py
# Purpose: # Main application for OrLit, providing a GUI for selecting source and target directories,
# moving PDF files, and managing recent directories. It integrates with the pdf_handler module
# to handle PDF organization and the directory_manager module to manage recent directory history.
# This script also handles the opening of an Excel file for literature organization and
# provides a user-friendly interface for managing literature files. 
# # This module serves as the entry point for the OrLit application.

# Copyright 2025 Aarush Jhaveri
# Copyright 2025 Goutam Narayan Tumulu
# Copyright 2025 Sanjay Mahajani
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from directory_manager2 import (
    get_recent_directories, save_recent_directory, SOURCE_HISTORY_FILE, TARGET_HISTORY_FILE
)
from pdf_handler import move_selected_pdfs
import subprocess
import threading
import time
import sys  # For PyInstaller compatibility
import psutil  # To close Excel
from ctypes import windll  # To set the taskbar icon on Windows

# --- Global Variables ---
stop_event = threading.Event()  # Event to stop the background process
background_thread = None  # Track the background thread

# 🎨 Palette Colors
BG_COLOR = "#264653"        # Background color (dark blue-green)
BUTTON_COLOR = "#F4A261"    # Accent button color
BUTTON_HOVER = "#E76F51"    # Hover color
TEXT_COLOR = "#FFFFFF"      # White text
FONT = ("Sans Serif", 12)

# Window Icon for OrLit
def get_icon_path():
    """Get the correct path for the icon in both development and PyInstaller build modes."""
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle
        return os.path.join(sys._MEIPASS, "OrLit_Icon.ico")
    else:
        # Development mode
        return os.path.join(os.path.dirname(__file__), "OrLit_Icon.ico")

# --- Utility Functions ---
def get_script_dir():
    """Returns the directory of the current script."""
    return os.path.dirname(os.path.abspath(__file__))

def close_excel():
    """Closes all open instances of Excel."""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == "excel.exe":
            proc.kill()

def browse_directory(entry_var, dropdown, history_file):
    """Opens file dialog for selecting a new directory, closes Excel, and updates dropdown."""
    close_excel()  # Close Excel as soon as Browse is clicked
    new_dir = filedialog.askdirectory(title="Select Directory")
    
    if new_dir:
        entry_var.set(new_dir)
        save_recent_directory(history_file, new_dir)
        update_dropdown(dropdown, new_dir, history_file)

def update_dropdown(dropdown, new_entry, history_file):
    """Adds newly selected directories to the dropdown list if not already present."""
    """Update dropdown values dynamically after browsing."""

    save_recent_directory(history_file, new_entry)  # Save it to JSON
    updated_history = get_recent_directories(history_file)
    dropdown['values'] = ["📂 Choose a New Directory"] + updated_history
    dropdown.set(new_entry)
    history = get_recent_directories(history_file)

    # Ensure no duplicates before inserting
    if new_entry in history:
        history.remove(new_entry)

    # Add new entry to the top
    history.insert(0, new_entry)

    # Keep only the last 5 entries
    history = history[:5]

def update_source_var(source_var, dropdown):
    """Updates source_var with the selected value from the dropdown."""
    source_var.set(dropdown.get())

def on_dropdown_select(entry_var, dropdown, history_file):
    """Closes Excel immediately when interacting with the dropdown."""
    close_excel()  # Close Excel as soon as the dropdown is clicked
    selected_value = dropdown.get()
    
    if selected_value == "📂 Choose a New Directory":
        browse_directory(entry_var, dropdown, history_file)
    else:
        entry_var.set(selected_value)
    
    dropdown.selection_clear()  # Ensure dropdown closes immediately

def select_pdfs_and_process(source_var, target_var):
    """Opens file dialog for selecting PDFs and sends them to pdf_handler.py."""
    pdf_files = filedialog.askopenfilenames(initialdir=source_var.get(), title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
    
    if pdf_files:
        move_selected_pdfs(pdf_files, target_var.get())  # Move and organize PDFs

def close_window(root):
    """Closes the Python application window only (does not close Excel)."""
    """Closes the Python application window only (does not close Excel)."""
    global stop_event, background_thread
    stop_event.set()  # Ensure the background thread terminates
    
    # Ensure the background thread terminates
    if background_thread and background_thread.is_alive():
        background_thread.join(timeout=5)

    root.quit()
    root.destroy()

def open_excel(target_var):
    """Opens the 'Literature Organisation.xlsx' file if it exists."""
    global stop_event
    stop_event.set()  # Stop the background process 
    print("Stopped background process")

    target_directory = target_var.get()
    excel_file = os.path.join(target_directory, "Literature Organisation.xlsx")

    if os.path.exists(excel_file):
        # Open Excel in a fully detached process
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        subprocess.Popen(
            ["start", "excel", excel_file],
            shell=True,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        )
    else:
        messagebox.showerror("Error", "Excel file not found")
    
    time.sleep(8)

def accept_changes(source_var, target_var, citation_style_var, source_dropdown, target_dropdown):
    global stop_event, background_thread
    stop_event.set()  # Stop the background process
    if background_thread and background_thread.is_alive():
        print("🛑 Waiting for previous background thread to terminate...")
        background_thread.join(timeout=5) # Ensure it fully terminates
    close_excel()

    save_recent_directory(SOURCE_HISTORY_FILE, source_var.get())
    save_recent_directory(TARGET_HISTORY_FILE, target_var.get())

    # ✅ Update dropdowns with the new history
    update_dropdown(source_dropdown, source_var.get(), SOURCE_HISTORY_FILE)
    update_dropdown(target_dropdown, target_var.get(), TARGET_HISTORY_FILE)

    stop_event.clear()  # Reset the stop event
    run_main_in_background(source_var, target_var, citation_style_var)

def run_main_in_background(source_var, target_var, citation_style_var):
    """Runs the main process in the background with proper termination."""
    global background_thread, stop_event

    from main7 import main

    def run_loop():
        """Runs the main process with a timeout check."""
        source_directory = source_var.get()
        target_directory = target_var.get()
        citation_style = citation_style_var.get()


        if source_directory == "📂 Choose a New Directory" or target_directory == "📂 Choose a New Directory":
            print("Warning", "⚠️ Please select valid source and target directories!")
            return

        print("🚀 Running main process...")

        # Loop with immediate stop on `stop_event`
        while not stop_event.is_set():
            try:
                main(source_directory, target_directory,citation_style)
                
                # Use `stop_event.wait()` instead of `time.sleep()` for immediate stop
                if stop_event.wait(timeout=10):  
                    print("🔴 Stop event triggered. Terminating thread...")
                    break

            except Exception as e:
                print(f"❌ Error: {e}")
                break

        print("✅ Background process stopped.")

    # Properly stop the old thread before starting a new one
    if background_thread and background_thread.is_alive():
        print("🛑 Terminating previous thread...")
        background_thread.join(timeout=5)

    # Create a new background thread
    background_thread = threading.Thread(target=run_loop, daemon=True)
    background_thread.start()

# --- UI Styling Functions ---
def on_enter(e):
    """Button hover effect."""
    e.widget.config(bg=BUTTON_HOVER)

def on_leave(e):
    """Button leave effect."""
    e.widget.config(bg=BUTTON_COLOR)

# --- Main UI Function ---
def select_directories():
    close_excel()
    """Displays a UI window for selecting Source & Target directories."""
    root = tk.Tk()
    root.title("OrLit: Simplify, Organize, Discover")
    root.configure(bg=BG_COLOR)  # Full background color
    root.geometry("800x350")  # Increased height for Close button
    root.resizable(False, False)

    # Set the custom icon
    icon_path = icon_path = get_icon_path()
    root.iconbitmap(icon_path)
    app_id = "OrLit.exe"  # Unique ID for taskbar icon
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    root.wm_iconbitmap(icon_path)

    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print("⚠️ Icon file not found. Using default icon.")
    
    #Style for labels
    label_style = {"bg": BG_COLOR, "fg": TEXT_COLOR, "font": ("Sans Serif", 13, "bold")}

    #Style for dropdowns
    dropdown_style = {"font": ("Sans Serif", 8)}

    #Style for buttons
    button_style = {"font": ("Sans Serif", 8), "bg": BUTTON_COLOR, "fg": BG_COLOR, "relief": "flat", "bd": 0, "width": 15, "height": 1}

    # Citation Style Selection
    tk.Label(root, text="Citation Style:", **label_style).grid(row=0, column=3, pady=10, padx=10, sticky="w")

    citation_styles = ["APA", "MLA 9", "ACS", "Chicago", "ASA", "Elsevier", "IEEE", "Nature"]
    citation_style_var = tk.StringVar(value="APA")

    citation_dropdown = ttk.Combobox(root, textvariable=citation_style_var, values=citation_styles, state="readonly", **dropdown_style, width=15)
    citation_dropdown.grid(row=1, column=3, pady=10, padx=10)

    # Load recent directories separately for source and target
    source_history = get_recent_directories(SOURCE_HISTORY_FILE)
    target_history = get_recent_directories(TARGET_HISTORY_FILE)

    # Use the most recent history as the default value if available
    default_source = source_history[0] if source_history else "📂 Choose a New Directory"
    default_target = target_history[0] if target_history else "📂 Choose a New Directory"

    # Source & Target Variables
    source_var = tk.StringVar(value=default_source)
    target_var = tk.StringVar(value=default_target)

    # Source Directory Selection
    tk.Label(root, text="Select Source Directory:", **label_style).grid(row=0, column=0, pady=10, padx=10, sticky="w")

    source_dropdown = ttk.Combobox(root, textvariable=source_var, values=["📂 Choose a New Directory"] + source_history, state="readonly", **dropdown_style, width = 40)
    source_dropdown.grid(row=0, column=1, pady=10, padx=10)
    
    # Added event binding to close Excel on dropdown click
    source_dropdown.bind("<Button-1>", lambda event: close_excel())

    # 🔥 Added binding to update source_var when dropdown is selected
    source_dropdown.bind("<<ComboboxSelected>>", lambda event: update_source_var(source_var, source_dropdown))

    source_button = tk.Button(root, text="Browse", **button_style, command=lambda: browse_directory(source_var, source_dropdown, SOURCE_HISTORY_FILE))
    
    # Added Excel close on Browse button click
    source_button.config(command=lambda: (close_excel(), browse_directory(source_var, source_dropdown, SOURCE_HISTORY_FILE)))
    
    source_button.grid(row=0, column=2, pady=10, padx=10)

    source_button.bind("<Enter>", on_enter)
    source_button.bind("<Leave>", on_leave)

    # Target Directory Selection
    tk.Label(root, text="Select Target Directory:", **label_style).grid(row=1, column=0, pady=10, padx=10, sticky="w")

    target_dropdown = ttk.Combobox(root, textvariable=target_var, values=["📂 Choose a New Directory"] + target_history, state="readonly", **dropdown_style, width=40)
    target_dropdown.grid(row=1, column=1, pady=10, padx=10)
    
    # Added event binding to close Excel on dropdown click
    target_dropdown.bind("<Button-1>", lambda event: close_excel())
    target_dropdown.bind("<<ComboboxSelected>>", lambda event: on_dropdown_select(target_var, target_dropdown, TARGET_HISTORY_FILE))

    target_button = tk.Button(root, text="Browse", **button_style, command=lambda: browse_directory(target_var, target_dropdown, TARGET_HISTORY_FILE))
    
    # Added Excel close on Browse button click
    target_button.config(command=lambda: (close_excel(), browse_directory(target_var, target_dropdown, TARGET_HISTORY_FILE)))
    
    target_button.grid(row=1, column=2, pady=10, padx=10)

    target_button.bind("<Enter>", on_enter)
    target_button.bind("<Leave>", on_leave)

    # Action Buttons (Move PDFs, Open Excel, Close)
    button_frame = tk.Frame(root, bg=BG_COLOR)
    button_frame.grid(row=2, column=0, columnspan=3, pady=20)

    pdf_button = tk.Button(button_frame, text="Move PDFs", **button_style, command=lambda: select_pdfs_and_process(source_var, target_var))
    pdf_button.grid(row=0, column=1, padx=10)

    excel_button = tk.Button(button_frame, text="Open Excel", **button_style, command=lambda: open_excel(target_var))
    excel_button.grid(row=0, column=2, padx=10)

    accept_button = tk.Button(button_frame, text="Accept Changes", **button_style, command=lambda: accept_changes(source_var, target_var, citation_style_var, source_dropdown, target_dropdown))
    accept_button.grid(row=0, column=0, padx=10)

    close_button = tk.Button(button_frame, text="Close App", **button_style, command=lambda: (close_window(root)))
    close_button.grid(row=0, column=3, padx=10)

    pdf_button.bind("<Enter>", on_enter)
    pdf_button.bind("<Leave>", on_leave)

    excel_button.bind("<Enter>", on_enter)
    excel_button.bind("<Leave>", on_leave)

    accept_button.bind("<Enter>", on_enter)
    accept_button.bind("<Leave>", on_leave)

    close_button.bind("<Enter>", on_enter)
    close_button.bind("<Leave>", on_leave)

    run_main_in_background(source_var, target_var, citation_style_var)

    root.mainloop()
    return source_var.get(), target_var.get()

# --- Run the UI ---
if __name__ == "__main__":
    select_directories()
