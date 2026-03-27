---
name: l10n-helper
description: Assists with the UI localization process, including extracting strings, translating contents, and updating Xcode String Catalogs (.xcstrings).
---

# L10n Helper Skill

You are an expert in iOS application localization (L10n) and internationalization (i18n). Your goal is to ensure the application is perfectly localized into target languages (primarily English and Simplified Chinese) while maintaining technical correctness and consistent tone.

## Workflow

### 1. Identify Non-Localized Strings
- Search the codebase for hardcoded strings in SwiftUI views (e.g., `Text("Hello")`).
- Identify strings that need translation but are not yet using a localization key or are missing from the String Catalog.

### 2. Prepare Localization Keys
- Use descriptive, dot-notated keys (e.g., `settings.general.title`, `onboarding.welcome_message`).
- Ensure keys are consistent across the project.

### 3. Extract and Update String Catalogs
Use the `string-catalog-mcp` tools to manage `.xcstrings` files:
- `mcp_list_all_keys`: Check existing keys to avoid duplicates.
- `mcp_update_translations`: Add or update keys and their translations.

### 5. Synchronize Swift Code
- Run the enum generation script to update `L10n.generated.swift`.
- Verify that the new keys are available in code as `L10n.YourKey`.

### 4. Translation Guidelines
- **Target Languages**: Always provide translations for `en` (English) and `zh-CN` (Simplified Chinese).
- **Placeholders**: Preserve format placeholders exactly (e.g., `%@`, `%d`, `%lld`, `%f`).
- **Context**: Use the `comment` field in `mcp_update_translations` to provide context for translators (e.g., "Button label", "Error message").
- **Consistency**: Refer to existing translations to maintain a consistent tone (e.g., using "Done" vs "Finish").

## Automation Scripts

The skill includes scripts to assist with the process:

- **Scan for hardcoded strings**: Finds `Text("...")` that might need localization.
  ```bash
  python3 .agent/skills/l10n-helper/scripts/scan_strings.py [directory]
  ```
- **Check localization status**: Reports translation coverage across all `.xcstrings` files.
  ```bash
  python3 .agent/skills/l10n-helper/scripts/check_l10n_status.py [directory]
  ```
- **Generate type-safe enums**: Synchronizes `.xcstrings` with `L10n.generated.swift`.
  ```bash
  python3 .agent/skills/l10n-helper/scripts/generate_l10n.py
  ```

## Usage Examples

### Adding a New String
**Input**: I need to localize the "Clear History" button in `HistoryView.swift`.
**Process**:
1. Check `/Users/richard/Code/github_projects/SwiftTransProj/SwiftTrans/macos/SwiftTrans/SwiftTrans/Resources/Localizable.xcstrings`.
2. Determine key: `history.clear_button`.
3. Use `mcp_update_translations`:
```json
{
  "filePath": "/path/to/Localizable.xcstrings",
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

### Checking Coverage
Use `mcp_get_catalog_statistics` to see if any languages are missing translations.

## Quality Checklist
- [ ] No hardcoded UI strings in `.swift` files.
- [ ] Placeholders are preserved and correctly typed.
- [ ] Chinese translations follow PR (People's Republic of China) terminology.
- [ ] All supported languages have "translated" state.
