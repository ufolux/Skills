#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime

# Get script and resource paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Template is in ../resources/license_header.swift.txt
RESOURCE_PATH = os.path.join(SCRIPT_DIR, '..', 'resources', 'license_header.swift.txt')

def get_header_template():
    try:
        with open(RESOURCE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading template from {RESOURCE_PATH}: {e}", file=sys.stderr)
        return None

def add_license_header(file_path, dry_run=False):
    ext = os.path.splitext(file_path)[1]
    # Only process .swift files as requested by user
    if ext != '.swift':
        return

    template = get_header_template()
    if not template:
        return
        
    header = template.format(year=datetime.now().year)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if "Licensed under the Apache License, Version 2.0" in content:
            # print(f"Skipping {file_path}: License already exists")
            return

        print(f"Adding license to {file_path}")
        if dry_run:
            return

        new_content = header + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Add Apache 2.0 license header to Swift source files.')
    parser.add_argument('path', help='File or directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    args = parser.parse_args()

    target = os.path.abspath(args.path)
    if os.path.isfile(target):
        add_license_header(target, args.dry_run)
    elif os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            # Skip hidden directories like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                add_license_header(os.path.join(root, file), args.dry_run)

if __name__ == "__main__":
    main()
