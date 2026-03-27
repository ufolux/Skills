#!/usr/bin/env python3
import json
import os
import sys

def check_l10n_status(root_dir):
    """
    Finds all .xcstrings files and reports translation coverage.
    """
    xcstrings_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".xcstrings"):
                xcstrings_files.append(os.path.join(root, file))

    if not xcstrings_files:
        print("No .xcstrings files found.")
        return

    print(f"Found {len(xcstrings_files)} String Catalog files:")
    for file_path in xcstrings_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            source_language = data.get("sourceLanguage", "en")
            strings = data.get("strings", {})
            total_keys = len(strings)
            
            # Get all languages present in the catalog
            languages = set()
            for key, info in strings.items():
                localizations = info.get("localizations", {})
                for lang in localizations.keys():
                    languages.add(lang)
            
            print(f"\nFile: {os.path.basename(file_path)}")
            print(f"  Source Language: {source_language}")
            print(f"  Total Keys: {total_keys}")
            
            for lang in sorted(languages):
                translated_count = 0
                for key, info in strings.items():
                    localizations = info.get("localizations", {})
                    loc = localizations.get(lang, {})
                    state = loc.get("stringUnit", {}).get("state")
                    if state in ["translated", "reviewed"]:
                        translated_count += 1
                
                percentage = (translated_count / total_keys * 100) if total_keys > 0 else 100
                print(f"  [{lang}] {translated_count}/{total_keys} ({percentage:.1f}%)")

        except Exception as e:
            print(f"  Error reading {file_path}: {e}")

if __name__ == "__main__":
    search_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    abs_search_dir = os.path.abspath(search_dir)
    check_l10n_status(abs_search_dir)
