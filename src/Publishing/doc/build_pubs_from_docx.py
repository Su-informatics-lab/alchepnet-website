#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build publications JSON directly from Word document
Each paragraph = one publication
"""
import json
import re
import sys
import os

def parse_docx_with_python_docx(filename):
    """Parse DOCX file using python-docx library"""
    try:
        from docx import Document
    except ImportError:
        print("❌ python-docx library not found.")
        print("Please install it: pip3 install python-docx")
        sys.exit(1)
    
    doc = Document(filename)
    
    pubs_by_year = {}
    current_year = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        if not text:
            continue
        
        # Check if this is a year header (only 4 digits)
        year_match = re.match(r'^(\d{4})$', text)
        if year_match:
            current_year = year_match.group(1)
            if current_year not in pubs_by_year:
                pubs_by_year[current_year] = []
            continue
        
        # If we have a current year and text is long enough, it's a publication
        if current_year and len(text) > 20:
            pubs_by_year[current_year].append({"content": text})
    
    return pubs_by_year

def main():
    if len(sys.argv) < 2:
        print("usage: python3 build_pubs_from_docx.py <word document path>")
        print("example: python3 build_pubs_from_docx.py 'Publication List in Descending Order.docx'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    print(f"reading Word document: {input_file}")
    
    try:
        pubs_by_year = parse_docx_with_python_docx(input_file)
    except Exception as e:
        print(f"error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if not pubs_by_year:
        print("no publications found")
        sys.exit(1)
    
    # Calculate total
    total_pubs = sum(len(pubs) for pubs in pubs_by_year.values())
    
    # Create output structure
    output = {
        "grantInfo": {
            "grantNumber": "U01AA026980",
            "pi": "McClain, Craig J.",
            "totalPublications": total_pubs
        },
        "publicationsByYear": pubs_by_year
    }
    
    # Write JSON
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'all_publications.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"success: {output_path}")
    print(f"total publications: {total_pubs}")
    
    # Show summary by year
    years = sorted(pubs_by_year.keys(), key=int, reverse=True)
    print(f"year range: {years[-1]} - {years[0]}")
    print("\npublications per year:")
    for year in years:
        print(f"  {year}: {len(pubs_by_year[year])}")

if __name__ == "__main__":
    main()