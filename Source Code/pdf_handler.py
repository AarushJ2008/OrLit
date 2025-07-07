# File: pdf_handler.py
# Purpose: Manage PDF files by moving them to folders based on their creation date.

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

def get_file_creation_date(file_path):
    """Returns the creation date of a file in 'MMM DD YYYY' format (e.g., Mar 11 2025)."""
    try:
        if sys.platform == "win32":  
            creation_timestamp = os.path.getctime(file_path)
        elif sys.platform == "darwin":  
            creation_timestamp = os.stat(file_path).st_birthtime
        else:  
            creation_timestamp = os.path.getmtime(file_path)

        return datetime.fromtimestamp(creation_timestamp).strftime('%b %d %Y')
    except Exception as e:
        print(f"⚠️ Error retrieving creation date for {file_path}: {e}")
        return "Unknown Date"  # Default folder if date retrieval fails

def move_selected_pdfs(pdf_files, target_folder):
    """Moves selected PDF files to their creation date folders in the target directory."""
    if not pdf_files or not target_folder:
        print("⚠️ No PDFs selected or target folder not set.")
        return

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for pdf in pdf_files:
        if not os.path.exists(pdf):
            print(f"❌ File not found: {pdf}")
            continue
        
        try:
            birthdate = get_file_creation_date(pdf)
            date_folder = os.path.join(target_folder, birthdate)

            if not os.path.exists(date_folder):
                os.makedirs(date_folder)  # Create folder for the birthdate if not exists

            new_pdf_path = os.path.join(date_folder, os.path.basename(pdf))
            shutil.move(pdf, new_pdf_path)
            print(f"📄 Moved PDF: {os.path.basename(pdf)} → {date_folder}")

        except Exception as e:
            print(f"❌ Error moving {pdf}: {e}")

# Do not execute automatically; just define the functions
