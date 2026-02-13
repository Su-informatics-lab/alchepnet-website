#!/usr/bin/env python3
"""
Update AlcHepNet website pages with dynamic navbar and footer
"""

import os
import re
import shutil
from pathlib import Path

def create_backup(file_path):
    """Create file backup"""
    backup_path = str(file_path) + '.backup'
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")

def extract_title_from_file(file_path):
    """Extract title from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find title tag
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                return title_match.group(1).strip()
            
            # Find h1 tag as fallback
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE)
            if h1_match:
                return h1_match.group(1).strip()
            
            # Find h2 tag as fallback
            h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE)
            if h2_match:
                return h2_match.group(1).strip()
            
            return "AlcHepNet"
    except Exception as e:
        print(f"Error extracting title from {file_path}: {e}")
        return "AlcHepNet"

def extract_main_content(file_path):
    """Extract main content from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find content within main tags
        main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL | re.IGNORECASE)
        if main_match:
            return main_match.group(1).strip()
        
        # If no main tag, find content within body tag (excluding header and footer)
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_content = body_match.group(1)
            # Remove header section
            body_content = re.sub(r'<header[^>]*>.*?</header>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
            # Remove footer section
            body_content = re.sub(r'<footer[^>]*>.*?</footer>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
            # Remove script tags
            body_content = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
            return body_content.strip()
        
        return ""
    except Exception as e:
        print(f"Error extracting content from {file_path}: {e}")
        return ""

def generate_new_html(file_path, title, main_content):
    """Generate new HTML content"""
    # Generate page description from filename
    filename = Path(file_path).stem
    description = filename.replace('-', ' ').title()
    
    new_html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="description" content="{description}">
  <meta name="author" content="AlcHepNet">
  <link rel="icon" href="favicon.ico">
  <title>{title}</title>
  <link href="bootstrap.min.css" rel="stylesheet">
  <link href="main.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
  <div id="navbar-include"></div>
  <div id="search-modal-include"></div>

  <main role="main">
    <div class="container marketing">
{main_content}
    </div>
  </main>

  <div id="footer-include"></div>

  <script src="popper.min.js"></script>
  <script src="bootstrap.min.js"></script>
  <script src="simple-dropdown.js"></script>
  <script>
    $(function() {{
      $("#navbar-include").load("navbar.html", function() {{
        console.log('Navbar loaded');
      }});
      $("#search-modal-include").load("search-modal.html");
      $("#footer-include").load("footer.html", function() {{
        console.log('Footer loaded');
      }});
    }});
  </script>
</body>
</html>'''
    
    return new_html

def update_html_file(file_path):
    """Update single HTML file"""
    print(f"Processing: {file_path}")
    
    # Skip already updated files
    if file_path.name in ['index.html', 'about.html', 'navbar.html', 'footer.html', 'search-modal.html']:
        print(f"Skipping already updated file: {file_path}")
        return
    
    # Skip backup files
    if file_path.name.endswith('.backup'):
        print(f"Skipping backup file: {file_path}")
        return
    
    # Skip template files
    if file_path.name in ['page-template.html', 'template-page.html']:
        print(f"Skipping template file: {file_path}")
        return
    
    # Skip maintenance pages
    if file_path.name in ['index-maintenance.html', 'quickstart.html']:
        print(f"Skipping maintenance file: {file_path}")
        return
    
    try:
        # Create backup
        create_backup(file_path)
        
        # Extract title and content
        title = extract_title_from_file(file_path)
        main_content = extract_main_content(file_path)
        
        # Generate new HTML
        new_html = generate_new_html(file_path, title, main_content)
        
        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        print(f"Updated: {file_path}")
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def main():
    """Main function"""
    # Fix: Use current directory instead of looking for src
    current_dir = Path(".")
    
    if not current_dir.exists():
        print("Error: Current directory not found!")
        return
    
    # Get all HTML files
    html_files = list(current_dir.glob("*.html"))
    
    print(f"Found {len(html_files)} HTML files")
    print("Starting batch update...")
    
    # Update each file
    for html_file in html_files:
        update_html_file(html_file)
    
    print("\nBatch update completed!")
    print("Note: Backup files have been created with .backup extension")

if __name__ == "__main__":
    main() 