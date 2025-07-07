# File: citation_parser2.py
# Purpose: Parse citation files to extract relevant bibliographic data.
# This module provides a function to parse citation files in various formats (e.g., RIS, BibTeX)
# and extract structured data such as authors, title, publication date, journal, volume, issue,
# pages, abstract, and DOI. It handles different citation formats and ensures the data is cleaned.

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

from datetime import datetime
import os
import sys
import re


def get_file_creation_date(file_path):
    """Get the file creation date cross-platform."""
    if sys.platform == "win32":  
        # Windows: Use getctime (creation time)
        creation_timestamp = os.path.getctime(file_path)
    elif sys.platform == "darwin":  
        # macOS: Use st_birthtime (actual file creation date)
        creation_timestamp = os.stat(file_path).st_birthtime
    else:  
        # Linux: No creation date, fallback to earliest modification time
        creation_timestamp = os.path.getmtime(file_path)

    return datetime.fromtimestamp(creation_timestamp).strftime('%b %d %Y')  # Format: Mar 11 2025

def parse_citation_file(citation_path):
    """Extract relevant data from a citation file."""
    access_date = get_file_creation_date(citation_path)  # Get the correct creation date

    data = {
        'Sr. No.': None, 
        'Authors': None,
        'Access Date': access_date,
        'Title': None,
        'First Author': None,
        'Last Author': None,
        'Publication Date': None,
        'Journal': None,
        'Volume': None,
        'Issue': None,
        'Pages': None,
        'Abstract': None,
        'DOI': None,
        'Remarks': None,
    }

    authors = []
    with open(citation_path, 'r', encoding='utf-8') as file:
        for line in file:
            #Extract Title
            if line.startswith(('T1  -', 'TI  -')):  
                data['Title'] = re.split(r'[-=]', line, 1)[-1].strip()
            elif line.startswith(('%T')):
                data['Title'] = re.split(r'[T]', line, 1)[-1].strip()
            elif line.startswith(('title =')):  
                data['Title'] = re.split(r'[{]', line, 1)[-1].strip()
            # Extract Authors
            elif line.startswith(('AU  -', 'FAU -','A1  -')):  
                authors.append(re.split(r'[-=]', line, 1)[-1].strip())
                data['Authors'] = authors
            elif line.startswith(('%A')):  
                authors.append(re.split(r'[=A]', line, 1)[-1].strip())
                data['Authors'] = authors
            elif line.strip().startswith('author ='):
                # Extract the part inside curly braces
                author_line = re.search(r'author\s*=\s*{(.+?)}', line, re.IGNORECASE)
                if author_line:
                    # Split by ' and ' (BibTeX format) and strip spaces
                    split_authors = [a.strip() for a in author_line.group(1).split(' and ')]
                    authors.extend(split_authors)
                    data['Authors'] = authors
            # Extract Publication Date
            elif line.startswith(('DA  -', 'DP  -','Y1  -')):  
                data['Publication Date'] = re.split(r'[-=]', line, 1)[-1].strip()
            elif line.startswith(('%D')):  
                data['Publication Date'] = re.split(r'[D]', line, 1)[-1].strip()
            elif 'year =' in line:
                 match = re.search(r'year\s*=\s*[{"](.+?)[}"]', line, re.IGNORECASE)
                 if match:
                    data['Publication Date'] = match.group(1).strip()
            # Extract Abstract
            elif line.startswith(('AB  -','N2  -')):  
                data['Abstract'] = re.split(r'[-=]', line, 1)[-1].strip()
            elif 'abstract =' in line:
                match = re.search(r'abstract\s*=\s*[{"](.+?)[}"]', line, re.IGNORECASE)
                if match:
                    data['Abstract'] = match.group(1).strip()
            # Extract DOI
            elif line.startswith(('DO  -','LID -')):
                raw_doi = re.split(r'[-=]', line, 1)[-1].strip()
                data['DOI'] = f"https://doi.org/{raw_doi}" if not raw_doi.startswith("http") else raw_doi
            elif line.startswith(('%M')):
                raw_doi = re.split(r'[M]', line, 1)[-1].strip()
                data['DOI'] = f"https://doi.org/{raw_doi}" if not raw_doi.startswith("http") else raw_doi
            elif 'doi =' in line:
                match = re.search(r'doi\s*=\s*[{"](.+?)[}"]', line, re.IGNORECASE)
                if match:
                    raw_doi = match.group(1).strip()
                    data['DOI'] = f"https://doi.org/{raw_doi}" if not raw_doi.startswith("http") else raw_doi
            # Extract Journal
            elif line.startswith(('JO  -', 'JT  -', 'JOUR -')):  
                data['Journal'] = re.split(r'[-=]', line, 1)[-1].strip()
            elif line.startswith(('PT -','%0')):  
                data['Journal'] = re.split(r'[-=0]', line, 1)[-1].strip()
            elif 'journal =' in line:
                match = re.search(r'journal\s*=\s*[{"](.+?)[}"]', line, re.IGNORECASE)
                if match:
                    data['Journal'] = match.group(1).strip()
            # Extract Volume
            elif line.startswith(('VL  -','VI -','volume =')):  
                data['Volume'] = re.split(r'[-=]', line, 1)[-1].strip()
            elif line.startswith(('%V')):  
                data['Volume'] = re.split(r'[V]', line, 1)[-1].strip()
            # Extract Issue
            elif line.startswith(('IP -','IS  -','number =')):  
                data['Issue'] = re.split(r'[-=]', line, 1)[-1].strip()
            elif line.startswith(('%N')):  
                data['Issue'] = re.split(r'[N]', line, 1)[-1].strip()
            # Extract Page Number
            elif line.startswith(('issn =','IS -','SN -')):  
                data['Pages'] = re.split(r'[-=]', line, 1)[-1].strip()
            elif line.startswith('%@ '):  
                data['Pages'] = re.split(r'[@]', line, 1)[-1].strip()
        
    if authors:
        data['First Author'] = authors[0]
        data['Last Author'] = authors[-1]

    # Remove curly braces and commas from all string fields
    for key in data:
        if isinstance(data[key], str):
            data[key] = re.sub(r'[{},\[\]]', '', data[key])

        elif isinstance(data[key], list):
            # Clean each author name in the list
            data[key] = [re.sub(r'[{},\[\]]', '', name) for name in data[key]]
  
    return data
