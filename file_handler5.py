# File: file_handler5.py
# Purpose: Manage file operations for the OrLit application, including moving citation files,
# selecting and moving PDFs, and organizing files by creation date. This module handles
# file transfers, ensures proper file handling, and provides user feedback through console messages.

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

import os
import shutil
import sys
from datetime import datetime
from tkinter import filedialog, messagebox, Tk


def get_directories():
    """Lazy import to avoid circular dependency"""
    from OrLit import select_directories
    return select_directories()

def list_citation_files(folder):
    """List all RIS, NBIB, BIB, and ENW citation files in a folder."""
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.ris', '.nbib', '.bib', '.enw'))]

def get_file_creation_date(file_path):
    """Get the file creation date cross-platform."""
    if sys.platform == "win32":  
        creation_timestamp = os.path.getctime(file_path)
    elif sys.platform == "darwin":  
        creation_timestamp = os.stat(file_path).st_birthtime
    else:  
        creation_timestamp = os.path.getmtime(file_path)

    return datetime.fromtimestamp(creation_timestamp).strftime('%b %d %Y')  # Format: Mar 11 2025

def move_files_to_target(source, target):
    """Moves only .ris, .nbib, .bib, and .enw files from the source to the target directory."""
    if not os.path.exists(source):
        print(f"⚠️ Source directory does not exist: {source}")
        return
    
    if not os.path.exists(target):
        os.makedirs(target)

    for item in os.listdir(source):
        src_path = os.path.join(source, item)
        dest_path = os.path.join(target, item)

        # Get file extension (lowercase for consistency)
        file_extension = os.path.splitext(item)[1].lower().strip()

        # Move only citation files
        if file_extension not in (".ris", ".nbib", ".bib", ".enw"):
            print(f"🚫 Skipping: {item} (Not a citation file)")
            continue  

        try:
            if os.path.isdir(src_path):  # Skip directories
                print(f"🚫 Skipping folder: {item}")
                continue
            else:  # Move only valid citation files
                shutil.move(src_path, dest_path)
                print(f"📄 Moved citation file: {item} → {target}")
        except Exception as e:
            print(f"❌ Error moving {item}: {e}")

def safe_move(src, dst):
    try:
        shutil.move(src, dst)
        return True
    except Exception as e:
        print(f"❌ Error moving {src} → {dst}: {e}")
        return False

def move_selected_pdfs(target):
    """Select and move multiple PDFs into date-organized folders in the target directory."""
    # Create root window (invisible, for dialogs)
    root = Tk()
    root.withdraw()

    pdf_files = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
    if not pdf_files:
        return

    failed_files = []

    for pdf in pdf_files:
        birthdate = get_file_creation_date(pdf)
        date_folder = os.path.join(target, birthdate)

        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        new_file_path = os.path.join(date_folder, os.path.basename(pdf))

        try:
            # Ensure file is not locked
            with open(pdf, "rb") as f:
                f.read(10)

            if safe_move(pdf, new_file_path):
                print(f"📄 Moved PDF: {os.path.basename(pdf)} → {date_folder}")
            else:
                failed_files.append(pdf)
                print(f"❌ Failed to move: {os.path.basename(pdf)}")

        except Exception as e:
            failed_files.append(pdf)
            print(f"❌ Cannot access {pdf}: {e}")

    if failed_files:
        failed_list = "\n".join([os.path.basename(f) for f in failed_files])
        messagebox.showerror(
            title="PDF Transfer Failed",
            message=(
                f"Some PDFs could not be moved:\n\n{failed_list}\n\n"
                "❗ Possible reasons:\n"
                "- The file is open in another program\n"
                "- The file is read-only or locked\n"
                "- It is stored on a synced/cloud folder (e.g., OneDrive)\n\n"
                "✅ Solutions:\n"
                "- Close the file in any open apps\n"
                "- Try moving from a local folder\n"
                "- Check file permissions"
            )
        )
    else:
        messagebox.showinfo("Success", "✅ All PDFs moved successfully!")

    root.destroy()

def organize_files_by_name(directory):
    """
    Organizes citation files AND their corresponding .txt files by the citation file's creation date.
    Pairs files with the same name together.
    """
    # Create a map of citation and .txt files by name
    citation_files = {}
    txt_files = {}

    # Collect all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        base_name, ext = os.path.splitext(filename)

        # Categorize files by extension
        if ext.lower() in ('.ris', '.nbib', '.bib', '.enw'):
            citation_files[base_name] = file_path
        elif ext.lower() == '.txt':
            txt_files[base_name] = file_path

    # Organize files together if they have matching names
    for base_name, citation_path in citation_files.items():
        # Get the matching .txt file
        txt_path = txt_files.get(base_name)

        # Use the creation date of the citation file for organization
        birthdate = get_file_creation_date(citation_path)
        date_folder = os.path.join(directory, birthdate)

        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        # Move citation file
        shutil.move(citation_path, os.path.join(date_folder, os.path.basename(citation_path)))
        print(f"📂 Organized {os.path.basename(citation_path)} → {date_folder}")

        # Move matching .txt file (if it exists)
        if txt_path and os.path.exists(txt_path):
            shutil.move(txt_path, os.path.join(date_folder, os.path.basename(txt_path)))
            print(f"📄 Organized {os.path.basename(txt_path)} → {date_folder}")

if __name__ == "__main__":
    source, target = get_directories()
    
    print(f"🔄 Moving files from {source} to {target} (excluding PDFs)...")
    move_files_to_target(source, target)
    
    print("📄 Selecting and moving PDFs...")
    move_selected_pdfs(target)

    print(f"🗂 Organizing files in {target} by citation file's creation date...")
    organize_files_by_name(target)

    print("✅ File organization complete!")