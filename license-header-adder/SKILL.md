---
name: license-header-adder
description: Assists with adding Apache 2.0 license headers to Swift source files. It uses a template stored in its resources directory.
---

# License Header Adder Skill

You are an expert in software compliance and project standardizations. Your goal is to ensure all Swift source files in the project carry the correct Apache 2.0 license header.

## Resources

- **License Template**: [license_header.swift.txt](file:///Users/richard/Code/github_projects/SwiftTransProj/SwiftTrans/.agent/skills/license-header-adder/resources/license_header.swift.txt)
  > [!IMPORTANT]
  > Always refer to this resource when manually adding headers or when the script needs the template.

## Workflow

### 1. Identify Files Missing Headers
- When creating a new Swift file, always add the license header immediately.
- Use the script to scan for missing headers in the `macos/` directory.

### 2. Apply the License Header
Use the provided automation script to prepend the license header to `.swift` files.

### 3. Verification
- Ensure the header is correctly placed at the beginning of the file.

## Usage

### Add license to a single Swift file
```bash
python3 .agent/skills/license-header-adder/scripts/add_license_header.py path/to/file.swift
```

### Add license to all Swift files in a directory
```bash
python3 .agent/skills/license-header-adder/scripts/add_license_header.py path/to/dir
```

### Preview changes (Dry Run)
```bash
python3 .agent/skills/license-header-adder/scripts/add_license_header.py path/to/dir --dry-run
```
