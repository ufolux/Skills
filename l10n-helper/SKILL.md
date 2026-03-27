---
name: l10n-helper
description: >
  Assists with iOS/macOS app localization using Xcode String Catalogs (.xcstrings).
  Handles the full workflow: scanning for hardcoded strings, managing localization keys,
  reading/updating translations, checking coverage, and generating type-safe Swift enums.
  Use this skill proactively whenever the user mentions localization, translation, l10n, i18n,
  .xcstrings files, String Catalogs, missing translations, hardcoded strings in SwiftUI,
  or wants to add/update strings for a new language.
---

# L10n Helper Skill

Expert in iOS/macOS app localization. Manages `.xcstrings` String Catalog files natively
via Python scripts — no MCP server or external tooling required.

## Available Scripts

All scripts live in `<skill-path>/scripts/`. Reference the skill's own directory when invoking:

```bash
SKILL=<path-to-skill>/l10n-helper/scripts

# Inspect a catalog
python3 $SKILL/xcstrings_tool.py list-languages path/to/Localizable.xcstrings
python3 $SKILL/xcstrings_tool.py statistics path/to/Localizable.xcstrings
python3 $SKILL/xcstrings_tool.py list-keys path/to/Localizable.xcstrings [--limit N] [--offset N]
python3 $SKILL/xcstrings_tool.py search-keys path/to/Localizable.xcstrings "query"
python3 $SKILL/xcstrings_tool.py get-key path/to/Localizable.xcstrings "some.key"

# Add or update translations
python3 $SKILL/xcstrings_tool.py update path/to/Localizable.xcstrings '{"data": [...]}'

# Scan Swift source for hardcoded strings
python3 $SKILL/scan_strings.py [directory]

# Check translation coverage across all .xcstrings files
python3 $SKILL/check_l10n_status.py [directory]

# Generate type-safe L10n.generated.swift enum from .xcstrings
python3 $SKILL/generate_l10n.py [--input-dir DIR] [--output FILE] [--dry-run] [--verify]
```

## Workflow

### 1. Find the String Catalog

First locate the `.xcstrings` file(s) in the project. Common locations:
- `<Target>/Resources/Localizable.xcstrings`
- `<Target>/Localizable.xcstrings`

Run `check_l10n_status.py` on the project root to find all catalogs and see coverage at a glance.

### 2. Identify Non-Localized Strings

- Run `scan_strings.py` to find `Text("hardcoded string")` patterns in Swift files.
- Look for strings not yet using a localization key or missing from the catalog.

### 3. Choose or Create Keys

Use descriptive, dot-notated keys that reflect the hierarchy of the UI:
- `settings.general.title`
- `history.clear_button`
- `onboarding.welcome_message`

Before creating a new key, check whether a similar one exists:
```bash
python3 $SKILL/xcstrings_tool.py search-keys Localizable.xcstrings "settings"
```

### 4. Add or Update Translations

Provide all target languages in one `update` call. The payload format:

```json
{
  "data": [
    {
      "key": "history.clear_button",
      "translations": [
        { "language": "en", "value": "Clear History" },
        { "language": "zh-CN", "value": "清除历史" }
      ],
      "comment": "Button label to delete all translation history"
    }
  ]
}
```

Pass inline:
```bash
python3 $SKILL/xcstrings_tool.py update Localizable.xcstrings '{"data": [...]}'
```

Or pass a JSON file:
```bash
python3 $SKILL/xcstrings_tool.py update Localizable.xcstrings translations.json
```

### 5. Verify Coverage

```bash
python3 $SKILL/xcstrings_tool.py statistics Localizable.xcstrings
```

All languages should show 100%.

### 6. Regenerate the Swift Enum (if the project uses one)

```bash
python3 $SKILL/generate_l10n.py --input-dir path/to/Resources --output path/to/L10n.generated.swift
```

This produces a type-safe `L10n` enum so keys are used as `L10n.History.clearButton` in code.

Verify the generated file is in sync:
```bash
python3 $SKILL/generate_l10n.py --input-dir path/to/Resources --verify
```

## Translation Guidelines

- **Target languages**: Always provide translations for every language already in the catalog. Check with `list-languages` first.
- **Placeholders**: Preserve `%@`, `%d`, `%lld`, `%f` exactly. Positional args (`%1$@`, `%2$@`) may be reordered to fit natural grammar.
- **Comments**: Use the `comment` field to give context to translators (e.g., "Button label", "Error message title").
- **Consistency**: Before translating, run `get-key` on related keys to match existing tone and terminology.
- **Chinese**: Use Simplified Chinese (zh-CN) with PRC terminology.

## Batch Translation Workflow

For translating many missing strings at once:

1. Run `statistics` to see which languages have gaps.
2. Run `list-keys` (with pagination if needed) to get all keys.
3. For each key that's missing translations, run `get-key` to see the source text.
4. Build a JSON payload with all missing translations and run `update` in one batch.

## Translation Review

When reviewing existing translations:

1. Use `statistics` to identify languages with lower coverage.
2. Use `list-keys` + `get-key` to inspect specific strings.
3. Check that placeholder counts match the source string.
4. Look for suspiciously short/long translations that might be truncated in the UI.
5. Fix any issues with `update` (passing `"state": "translated"` to mark them correct).

## Quality Checklist

- [ ] No hardcoded UI strings in `.swift` files.
- [ ] All keys present in all supported languages.
- [ ] Placeholders preserved and correctly typed in all translations.
- [ ] `comment` field filled for context-dependent strings.
- [ ] `L10n.generated.swift` regenerated after adding new keys.
