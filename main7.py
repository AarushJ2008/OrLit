# File: main7.py
# Purpose: Main script to manage citation files, organize them, and update an Excel file with bibliographic data.
# This script handles moving files from a source directory to a target directory, parsing citation files,
# generating citations, and updating an Excel file with the parsed data. It also saves new titles to a JSON file
# and organizes files by their creation date. 

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

import sys
import os
from file_handler5 import list_citation_files, organize_files_by_name, move_files_to_target
from excel_manager7 import load_or_create_excel, append_data_to_excel
from citation_parser2 import parse_citation_file
from citation_generator import generate_citation
from utils import is_file_open
import config
import json
import psutil
import time

def close_excel(output_file_path):
    """
    Closes the Excel file with the specified file path if it is open.
    
    Args:
        output_file_path (str): The full path of the Excel file to close.
    """
    # Extract the Excel file name from the path
    excel_file_name = os.path.basename(output_file_path)

    # Check for open Excel processes
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        if proc.info['name'].lower() == "excel.exe":
            try:
                open_files = proc.open_files()
                for file in open_files:
                    if excel_file_name in file.path:
                        print(f"✅ Closing {excel_file_name}...")
                        proc.terminate()
                        time.sleep(2)  # Ensure Excel fully closes
                        print(f"✅ {excel_file_name} closed successfully.")
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    print(f"ℹ️ {excel_file_name} was not open or already closed.")

# JSON cache file path
CACHED_TITLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "titles_cache.json")
def save_titles_to_json(new_titles):
    """Append new titles to the existing JSON file."""
    
    # Load existing titles from JSON if the file exists
    if os.path.exists(CACHED_TITLES):
        with open(CACHED_TITLES, "r", encoding="utf-8") as f:
            try:
                existing_titles = set(json.load(f))
            except json.JSONDecodeError:
                existing_titles = set()
    else:
        existing_titles = set()

    # Combine existing and new titles
    combined_titles = existing_titles.union(new_titles)

    # Save the merged titles back to the JSON file
    with open(CACHED_TITLES, "w", encoding="utf-8") as f:
        json.dump(list(combined_titles), f, ensure_ascii=False, indent=4)

def main(source_directory, target_directory, citation_style_var):
    print(f"Citation Style: {citation_style_var}")
    """Main function to process citation files, move them to target, and store titles in JSON."""

    if not source_directory or source_directory == "📂 Choose a New Directory":
        print("❌ No source directory selected. Exiting...")
        sys.exit(1)

    if not target_directory or target_directory == "📂 Choose a New Directory":
        print("❌ No target directory selected. Exiting...")
        sys.exit(1)

    # Move files from source to target directory
    print(f"🔄 Moving files from {source_directory} to {target_directory}...")
    move_files_to_target(source_directory, target_directory)

    # Excel file path
    script_directory = os.path.dirname(os.path.abspath(__file__))  
    output_file_path = os.path.join(target_directory, "Literature Organisation.xlsx")

    # Load or create the Excel file
    wb, ws = load_or_create_excel(output_file_path)

    # Get citation files (.ris, .nbib) from the target directory
    citation_files = list_citation_files(target_directory)

    new_data = []
    new_titles = set()
    citation_paths = {}

    for file in citation_files:
        # Extract filename without extension
        base_filename = os.path.splitext(os.path.basename(file))[0]

        extracted_data = parse_citation_file(file)

        # Add new entries to list
        if extracted_data['Title'] not in CACHED_TITLES:
            new_data.append(extracted_data)
            new_titles.add(extracted_data['Title'])

            # Generate citation
            intext_citation, bib_reference = generate_citation(extracted_data, citation_style_var)

            # Create .txt file with the same name as the citation file
            txt_filename = f"{base_filename}.txt"
            txt_file_path = os.path.join(target_directory, txt_filename)

            # Write citations to the .txt file
            with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(f"------------In Text Citation------------\n {intext_citation}\n\n\n\n\n\n\n")
                txt_file.write(f"------------Bibliography Reference------------\n {bib_reference}\n")
            
            citation_paths[extracted_data['Title']] = txt_filename

    # Append new data to Excel file
    if new_data:
        append_data_to_excel(output_file_path, ws, wb, new_data, target_directory, citation_paths)
        print(f"✅ Successfully updated {config.EXCEL_FILENAME} with new citations.")
    else:
        print("ℹ️ No new entries found. All citation files were duplicates.")

    wb.save(output_file_path)

    # Save the new titles to JSON
    print(f"💾 Saving {len(new_titles)} new titles to JSON...")
    save_titles_to_json(new_titles)

    # Organize files into folders by creation date
    print(f"📂 Organizing files in {target_directory} by creation date...")
    organize_files_by_name(target_directory)

    print("✅ File organization complete!")

    # Save all new data to a JSON file 
    script_directory = os.path.dirname(os.path.abspath(__file__))  
    data_file_path = os.path.join(script_directory, "data.json")

    # Load existing data if the file exists
    if os.path.exists(data_file_path):
        with open(data_file_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Ensure existing_data is a list
    if not isinstance(existing_data, list):
        existing_data = []

    # Append the new data to the existing list
    existing_data.extend(new_data)

    # Write the combined data back to the JSON file
    with open(data_file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

    # Target Directory Path File
    target_directory_path_file = os.path.join(script_directory, "target directory path file.txt")

    with open(target_directory_path_file, "w") as f:
        f.write(target_directory)
    

if __name__ == "__main__":
    main()