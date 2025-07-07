# File: citation_generator.py
# Purpose: Generate citations in various styles based on parsed data.
# This module provides a function to generate citations in APA, MLA, Chicago, ACS, ASA,
# Elsevier, IEEE, and Nature styles based on the provided data dictionary.
# It formats the citation strings according to the selected style and returns both in-text
# and bibliography references.

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

from tkinter import messagebox

def generate_citation(data, citation_type):
    """Generate and copy citation based on the selected style and type."""
    style = citation_type  # get style directly from dropdown
    matching_record = (data)
  # Define matching_record as an empty dictionary or fetch it from the appropriate source
    if not matching_record:
        messagebox.showwarning("No Match", "No matching record found.")
        return

    # Extract common fields (adjust formatting as needed)
    authors_list = matching_record.get("Authors", [])
    authors = ", ".join(authors_list) if isinstance(authors_list, list) else authors_list
    first_author = matching_record.get("First Author", "Unknown")
    date = matching_record.get("Publication Date", "n.d.")
    title = matching_record.get("Title", "Untitled")
    journal = matching_record.get("Journal", "Unknown Journal")
    volume = matching_record.get("Volume", "")
    issue = matching_record.get("Issue", "")
    pages = matching_record.get("Pages", "")
    doi = matching_record.get("DOI", "")

    # Initialize citation string
    citation_intext = ""
    citation_bib = ""

    # --- APA (7th edition) ---
    if style == "APA":
        citation_intext = f"({first_author}, {date})"
        # Example: Smith, J. (2020). Title of article. Journal Name, 12(3), 45-67. https://doi.org/xxx
        citation_bib = f"{authors} ({date}). {title}. {journal}, {volume}"
        if issue:
            citation_bib += f"({issue})"
        if pages:
            citation_bib += f", {pages}"
        if doi:
            citation_bib += f". https://doi.org/{doi}"
    
    # --- MLA 9 ---
    elif style == "MLA 9":
        citation_intext = f"({first_author})"
        # Example: Smith, John. "Title of Article." Journal Name, vol. 12, no. 3, 2020, pp. 45-67, doi:xxx.
        citation_bib = f"{authors}. \"{title}.\" {journal}, vol. {volume}, no. {issue}, {date}, pp. {pages}"
        if doi:
            citation_bib += f", doi:{doi}."
        else:
            citation_bib += "."
    
    # --- Chicago (Author-Date) ---
    elif style == "Chicago":
        citation_intext = f"({first_author} {date})"
        # Example: Smith, John. 2020. "Title of Article." Journal Name 12, no. 3: 45-67. https://doi.org/xxx.
        citation_bib = f"{authors}. {date}. \"{title}.\" {journal} {volume}, no. {issue}: {pages}."
        if doi:
            citation_bib += f" https://doi.org/{doi}"
    
    # --- ACS (American Chemical Society) ---
    elif style == "ACS":
        citation_intext = f"({first_author}, {date})"
        # Example: Smith, John; Doe, Jane. Title of Article. Journal Name 2020, 12 (3), 45-67. doi:xxx.
        citation_bib = f"{authors}. {title}. {journal} {date}, {volume}"
        if issue:
            citation_bib += f"({issue})"
        if pages:
            citation_bib += f", {pages}"
        if doi:
            citation_bib += f". doi:{doi}"
    
    # --- ASA ---
    elif style == "ASA":
        citation_intext = f"({first_author} {date})"
        # Example: Smith, John. 2020. "Title of Article." Journal Name 12(3): 45-67. doi:xxx.
        citation_bib = f"{authors}. {date}. \"{title}.\" {journal} {volume}"
        if issue:
            citation_bib += f"({issue})"
        if pages:
            citation_bib += f": {pages}"
        if doi:
            citation_bib += f". doi:{doi}"
    
    # --- Elsevier ---
    elif style == "Elsevier":
        citation_intext = f"({first_author}, {date})"
        # Elsevier journals often use a modified Vancouver style. Example:
        # Smith J, Doe J. Title of article. Journal Name. 2020;12(3):45-67. doi:xxx.
        citation_bib = f"{authors}. {title}. {journal}. {date};{volume}"
        if issue:
            citation_bib += f"({issue})"
        if pages:
            citation_bib += f":{pages}"
        if doi:
            citation_bib += f". doi:{doi}"
    
    # --- IEEE ---
    elif style == "IEEE":
        # IEEE in-text citations are typically numerical, but here we use a text version.
        citation_intext = f"[{first_author}, {date}]"
        # Example: J. Smith and J. Doe, "Title of article," Journal Name, vol. 12, no. 3, pp. 45-67, 2020.
        citation_bib = f"{authors}, \"{title},\" {journal}, vol. {volume}, no. {issue}, pp. {pages}, {date}."
        if doi:
            citation_bib += f" doi:{doi}"
    
    # --- Nature ---
    elif style == "Nature":
        # Nature in-text citations often appear as superscript numbers; we provide a text approximation.
        citation = f"{first_author} {date}"
        # Example: Smith J, Doe J. Title of article. Journal Name 12, 45–67 (2020). doi:xxx.
        citation = f"{authors}. {title}. {journal} {volume}, {pages} ({date})."
        if doi:
            citation += f" doi:{doi}"

    return citation_intext, citation_bib 