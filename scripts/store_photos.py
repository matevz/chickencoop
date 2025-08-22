#!/usr/bin/python

import argparse
import requests
import os
import sys
import time
from urllib.parse import urlparse
from datetime import datetime

# Minimum number of seconds between consecutive photos.
CAPTURE_EVERY = 10

parser = argparse.ArgumentParser(description="""
    Store photos from webcam URLs at regular intervals.
    
    This script continuously downloads images from the provided webcam URLs
    and stores them in organized directory structures (service/date/time.jpg).
    
    Usage examples:
      python store_photos.py https://example.com/webcam.jpg
      python store_photos.py https://cam1.example.com/image.jpg https://cam2.example.com/photo.jpg
      python store_photos.py -o /path/to/storage https://webcam.example.com/current.jpg
    
    The script will:
    - Create directories based on the service hostname and current date
    - Download images every {} seconds
    - Save images with timestamp filenames (HH-MM-SS.jpg)
    - Handle network errors gracefully and continue operation
    """.format(CAPTURE_EVERY))
parser.add_argument('urls', nargs='+', help='One or more URLs to capture photos from')
parser.add_argument('-o', '--output', default='.', help='Output folder (default: current directory)')
parser.add_argument('-i', '--interval', type=int, default=CAPTURE_EVERY, help=f'Interval between captures in seconds (default: {CAPTURE_EVERY})')
args = parser.parse_args()

# Use the parsed output directory
output_dir = args.output

while True:
    begin_time = datetime.now()
    for raw_service in args.urls:
        try:
            parsed = urlparse(raw_service)
            if not all([parsed.scheme, parsed.netloc]):
                print(f"Error: '{raw_service}' is not a valid URL")
                continue
        except Exception as e:
            print(f"Error: '{raw_service}' is not a valid URL: {e}")
            continue

        s = parsed.netloc

        # Get current date and time
        now = datetime.now()
        date_folder = now.strftime("%Y-%m-%d")
        time_filename = now.strftime("%H-%M-%S")

        # Create directory structure: service_name/date/
        service_dir = os.path.join(args.output, s, date_folder)
        os.makedirs(service_dir, exist_ok=True)

        # Download the image
        try:
            response = requests.get(raw_service, timeout=60)
            response.raise_for_status()

            # Save the image with timestamp filename
            filename = f"{time_filename}.jpg"
            filepath = os.path.join(service_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"Downloaded {s}: {filepath}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading from {s}: {e}")
    elapsed_time = (datetime.now() - begin_time).total_seconds()
    if elapsed_time < CAPTURE_EVERY:
        time.sleep(CAPTURE_EVERY - elapsed_time)