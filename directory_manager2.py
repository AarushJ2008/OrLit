# File: directory_manager2.py 
# Purpose: This module manages the history of recently used source and target directories
# for the OrLit application. It provides functions to save, load, and retrieve
# recent directory paths, storing them in JSON files within the user's home directory.

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
import json
import sys

# History file names
SOURCE_HISTORY_FILE = "source_history.json"
TARGET_HISTORY_FILE = "target_history.json"
MAX_HISTORY = 5  # Number of recent directories to store

def get_history_file_path(file_name):
    """Return full path to a history file stored in the user's home directory."""
    app_dir = os.path.join(os.path.expanduser("~"), ".orlit")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, file_name)

def load_recent_directories(file_name):
    """Load the list of recent directories from a JSON file."""
    file_path = get_history_file_path(file_name)
    
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def save_recent_directory(file_name, new_dir):
    # History file names
    SOURCE_HISTORY_FILE = "source_history.json"
    TARGET_HISTORY_FILE = "target_history.json"
    MAX_HISTORY = 5  # Number of recent directories to store

    # ✅ Prevent saving placeholders or empty entries
    if not new_dir or new_dir.strip() == "" or new_dir == "📂 Choose a New Directory":
        return

    """Save a new directory to the recent history, ensuring the most recent is at the top."""
    dirs = load_recent_directories(file_name)

    # Remove the directory if it already exists
    if new_dir in dirs:
        dirs.remove(new_dir)

    # Add the new directory at the beginning
    dirs.insert(0, new_dir)

    # Keep only the latest MAX_HISTORY entries
    dirs = dirs[:MAX_HISTORY]

    # Save the updated history back to the file
    file_path = get_history_file_path(file_name)
    with open(file_path, "w") as file:
        json.dump(dirs, file, indent=4)


def get_recent_directories(file_name):
    """Return the recent directories, ensuring the file exists."""
    return load_recent_directories(file_name)
