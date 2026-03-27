#!/usr/bin/env python3
"""
xcstrings_tool.py — Manage Xcode String Catalog (.xcstrings) files

Provides the same functionality as the string-catalog-mcp, but runs natively
as a Python script with no external dependencies or server setup required.

Usage:
  python3 xcstrings_tool.py list-languages <file.xcstrings>
  python3 xcstrings_tool.py statistics <file.xcstrings>
  python3 xcstrings_tool.py list-keys <file.xcstrings> [--limit N] [--offset N]
  python3 xcstrings_tool.py search-keys <file.xcstrings> <query>
  python3 xcstrings_tool.py get-key <file.xcstrings> <key>
  python3 xcstrings_tool.py update <file.xcstrings> <json_or_json_file>
"""

import json
import sys
import argparse
from pathlib import Path


def load_catalog(file_path: str) -> dict:
    path = Path(file_path).resolve()
    if not path.exists():
        print(json.dumps({"error": f"File not found: {file_path}"}))
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_catalog(file_path: str, data: dict):
    path = Path(file_path).resolve()
    sorted_strings = dict(sorted(data["strings"].items()))
    output = {"sourceLanguage": data["sourceLanguage"], "strings": sorted_strings}
    if "version" in data:
        output["version"] = data["version"]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_all_languages(data: dict) -> list:
    languages = {data["sourceLanguage"]}
    for entry in data.get("strings", {}).values():
        for lang in entry.get("localizations", {}).keys():
            languages.add(lang)
    return sorted(languages)


def get_string_unit_state(loc: dict) -> str:
    """Extract state from a localization entry, handling both stringUnit and plural variations."""
    su = loc.get("stringUnit", {})
    if su:
        return su.get("state", "")
    plural = loc.get("variations", {}).get("plural", {})
    primary = plural.get("other") or plural.get("one") or plural.get("zero")
    if primary:
        return primary.get("stringUnit", {}).get("state", "")
    return ""


def cmd_list_languages(args):
    data = load_catalog(args.file)
    languages = get_all_languages(data)
    print(json.dumps({
        "sourceLanguage": data["sourceLanguage"],
        "supportedLanguages": languages,
        "count": len(languages),
    }, indent=2))


def cmd_statistics(args):
    data = load_catalog(args.file)
    languages = get_all_languages(data)
    strings = data.get("strings", {})
    total_keys = len(strings)

    coverage = {}
    for lang in languages:
        translated = sum(
            1 for entry in strings.values()
            if get_string_unit_state(entry.get("localizations", {}).get(lang, {})) == "translated"
        )
        coverage[lang] = {
            "translated": translated,
            "total": total_keys,
            "percentage": round(translated / total_keys * 100) if total_keys > 0 else 0,
        }

    print(json.dumps({
        "totalKeys": total_keys,
        "languages": languages,
        "translationCoverage": coverage,
    }, indent=2))


def cmd_list_keys(args):
    data = load_catalog(args.file)
    all_keys = sorted(data.get("strings", {}).keys())
    paginated = all_keys[args.offset:args.offset + args.limit]
    print(json.dumps({
        "keys": paginated,
        "total": len(all_keys),
        "offset": args.offset,
        "limit": args.limit,
        "hasMore": args.offset + args.limit < len(all_keys),
    }, indent=2))


def cmd_search_keys(args):
    data = load_catalog(args.file)
    query = args.query.lower()
    matching = [k for k in sorted(data.get("strings", {}).keys()) if query in k.lower()]
    print(json.dumps({
        "query": args.query,
        "matchingKeys": matching,
        "count": len(matching),
    }, indent=2))


def cmd_get_key(args):
    data = load_catalog(args.file)
    entry = data.get("strings", {}).get(args.key)
    if entry is None:
        print(json.dumps({"error": f'Key "{args.key}" not found in catalog'}))
        sys.exit(1)

    translations = []
    for lang, loc in sorted(entry.get("localizations", {}).items()):
        su = loc.get("stringUnit", {})
        if su:
            translations.append({"language": lang, "value": su.get("value", ""), "state": su.get("state", "")})
        else:
            plural = loc.get("variations", {}).get("plural", {})
            primary = plural.get("other") or plural.get("one") or plural.get("zero")
            if primary:
                psu = primary.get("stringUnit", {})
                translations.append({"language": lang, "value": f"[plural] {psu.get('value', '')}", "state": psu.get("state", "")})

    print(json.dumps({
        "key": args.key,
        "comment": entry.get("comment", ""),
        "sourceLanguage": data["sourceLanguage"],
        "translations": translations,
    }, indent=2))


def cmd_update(args):
    data = load_catalog(args.file)

    raw = args.data
    try:
        payload = json.loads(raw) if raw.strip().startswith(("{", "[")) else json.loads(Path(raw).read_text())
    except Exception as e:
        print(json.dumps({"error": f"Failed to parse JSON: {e}"}))
        sys.exit(1)

    entries = payload.get("data", payload) if isinstance(payload, dict) else payload

    updated, created = [], []
    strings = data.setdefault("strings", {})

    for item in entries:
        key = item["key"]
        if key not in strings:
            strings[key] = {}
            created.append(key)
        else:
            updated.append(key)

        entry = strings[key]
        if "comment" in item:
            entry["comment"] = item["comment"]

        locs = entry.setdefault("localizations", {})
        for t in item.get("translations", []):
            locs[t["language"]] = {
                "stringUnit": {
                    "state": t.get("state", "translated"),
                    "value": t["value"],
                }
            }

    save_catalog(args.file, data)
    print(json.dumps({
        "success": True,
        "updatedKeys": updated,
        "createdKeys": created,
        "totalUpdated": len(updated),
        "totalCreated": len(created),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Manage Xcode String Catalog (.xcstrings) files")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-languages", help="List all languages in the catalog")
    p.add_argument("file", help="Path to .xcstrings file")

    p = sub.add_parser("statistics", help="Get translation coverage statistics per language")
    p.add_argument("file", help="Path to .xcstrings file")

    p = sub.add_parser("list-keys", help="List all localization keys (supports pagination)")
    p.add_argument("file", help="Path to .xcstrings file")
    p.add_argument("--limit", type=int, default=100, help="Max keys to return (default: 100)")
    p.add_argument("--offset", type=int, default=0, help="Keys to skip for pagination (default: 0)")

    p = sub.add_parser("search-keys", help="Search for keys containing a substring (case-insensitive)")
    p.add_argument("file", help="Path to .xcstrings file")
    p.add_argument("query", help="Substring to search for")

    p = sub.add_parser("get-key", help="Get all translations for a specific key")
    p.add_argument("file", help="Path to .xcstrings file")
    p.add_argument("key", help="The localization key to look up")

    p = sub.add_parser("update", help="Add or update translations in the catalog")
    p.add_argument("file", help="Path to .xcstrings file")
    p.add_argument(
        "data",
        help='JSON string or path to JSON file. Format: {"data": [{"key": "...", "translations": [{"language": "en", "value": "..."}]}]}'
    )

    args = parser.parse_args()
    {
        "list-languages": cmd_list_languages,
        "statistics": cmd_statistics,
        "list-keys": cmd_list_keys,
        "search-keys": cmd_search_keys,
        "get-key": cmd_get_key,
        "update": cmd_update,
    }[args.command](args)


if __name__ == "__main__":
    main()
