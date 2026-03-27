#!/usr/bin/env python3
import subprocess
import re
import sys
import os

def scan_for_strings(directory):
    """
    Scans Swift files for hardcoded Text("...") strings using ripgrep.
    """
    # Pattern for Text("...") where content is a literal string
    # Try to ignore Text(variable) or Text(localizedStringKey) if they don't have quotes
    # This regex is a simple heuristic.
    pattern = r'Text\s*\(\s*"([^"]+)"\s*\)'
    
    try:
        # Use ripgrep to find matches
        # -n: show line number
        # -H: show filename
        # --type swift
        result = subprocess.run(
            ['rg', '-n', '-H', '--type', 'swift', pattern, directory],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0 and result.stderr:
            print(f"Error running ripgrep: {result.stderr}", file=sys.stderr)
            return

        lines = result.stdout.strip().split('\n')
        if not lines or (len(lines) == 1 and not lines[0]):
            print("No hardcoded Text strings found.")
            return

        print(f"Found {len(lines)} potential hardcoded strings:")
        for line in lines:
            print(line)

    except FileNotFoundError:
        print("Error: ripgrep (rg) not found. Please install it.", file=sys.stderr)

if __name__ == "__main__":
    search_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    abs_search_dir = os.path.abspath(search_dir)
    print(f"Scanning directory: {abs_search_dir}")
    scan_for_strings(abs_search_dir)
