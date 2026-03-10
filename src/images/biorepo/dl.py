#!/usr/bin/env python3

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# target directory
TARGET_DIR = "/Users/bearbbcjtc/Alchepnet_website_gitrepo/alchepnet-website/src/images/biorepo"
SOURCE_URL = "https://indianabiobank.org/meet-our-staff.html"

# members list
MEMBERS = [
    "Tatiana-Foroud",
    "Brooke-Patz",
    "Whitney-Jaunzemis",
    "Ernest-Attakora",
    "Cheryl-Halter",
    "Jacob-Lee",
    "Becky-Long",
    "Ashley-Mayfield",
    "Jessica-Ross",
    "Michael-Aikin",
    "Kennedi-Burroughs",
    "Erin-Koehler",
    "Fatma-Niang",
    "Antonia-Walker",
    "Kailee-Woodall"
]

def download_image(url, filepath):
    """download image to specified path"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ downloaded: {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"✗ download failed {os.path.basename(filepath)}: {e}")
        return False

def find_images_on_page(url):
    """extract all image URLs from the webpage"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images = []
        
        # find all image tags
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # convert to absolute URL
                absolute_url = urljoin(url, src)
                alt = img.get('alt', '')
                images.append((absolute_url, alt))
        
        return images
    except Exception as e:
        print(f"✗ cannot access webpage: {e}")
        return []

def main():
    # create target directory
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"target directory: {TARGET_DIR}\n")
    
    # get all images on the webpage
    print("analyzing webpage...")
    images = find_images_on_page(SOURCE_URL)
    
    if not images:
        print("\ncannot extract images from the webpage automatically.")
        print("please manually download images, steps如下：")
        print("\n1. visit: https://indianabiobank.org/meet-our-staff.html")
        print("2. right click on each member's photo")
        print("3. select 'save as' or 'save image'")
        print("4. save to the following folder:")
        print(f"   {TARGET_DIR}")
        print("\nneeded file names:")
        for member in MEMBERS:
            print(f"   - {member}.jpg")
        return
    
    print(f"found {len(images)} images\n")
    
    # try to match and download
    downloaded = 0
    for member_name in MEMBERS:
        # try to find matching image
        found = False
        for img_url, alt_text in images:
            # check if URL or alt text contains member name
            name_parts = member_name.replace('-', ' ').split()
            if any(part.lower() in img_url.lower() or part.lower() in alt_text.lower() 
                   for part in name_parts if len(part) > 3):
                filepath = os.path.join(TARGET_DIR, f"{member_name}.jpg")
                if download_image(img_url, filepath):
                    downloaded += 1
                    found = True
                    break
        
        if not found:
            print(f"image not found for {member_name}")
    
    print(f"\ndone! downloaded {downloaded}/{len(MEMBERS)} images")
    
    if downloaded < len(MEMBERS):
        print("\nsome images need to be downloaded manually.")
        print("please visit the webpage and manually save the remaining images.")

if __name__ == "__main__":
    main()
    