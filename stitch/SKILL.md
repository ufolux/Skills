---
name: stitch
description: "Interact with Google Stitch to create and manage UI design projects. Use `uvx mcp2cli --mcp https://stitch.googleapis.com/mcp` for all Stitch operations: creating projects, generating screens from text prompts, editing screens, and generating design variants."
---

# Stitch Skill

Use `uvx mcp2cli` to interact with the [Stitch](https://stitch.withgoogle.com) MCP server at `https://stitch.googleapis.com/mcp`. Stitch is a Google tool that generates UI designs and screens from text prompts.

The base command for all operations is:
```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp
```

Discover all available commands:
```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp --list
```

## Concepts

- **Project**: A container for UI designs. Has a name and ID (e.g. `4044680601076201931`).
- **Screen**: A single UI screen within a project. Has a screen ID (e.g. `98b50e2ddc9943efb387052637738f61`).
- **Resource names**: Use the full resource name format `projects/{project}` or `projects/{project}/screens/{screen}` for `--name` parameters. Use the bare IDs (without prefix) for `--project-id` and `--screen-id` parameters.

## Workflows

### 1. List your projects

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp list-projects
# Show only owned projects (default):
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp list-projects --filter "view=owned"
# Show projects shared with you:
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp list-projects --filter "view=shared"
```

### 2. Create a new project

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp create-project --title "My App UI"
```

Note the returned project ID — you'll need it for all subsequent operations.

### 3. Generate a screen from a text prompt

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp generate-screen-from-text \
  --project-id "4044680601076201931" \
  --prompt "A mobile login screen with email and password fields, a sign-in button, and a forgot password link" \
  --device-type MOBILE
```

Device type options: `MOBILE`, `DESKTOP`, `TABLET`, `AGNOSTIC`.  
Model options: `GEMINI_3_PRO` (default quality), `GEMINI_3_FLASH` (faster).

**Important**: Generation can take a few minutes. Do not retry if it appears slow — check with `get-screen` afterward if the call times out.

### 4. List screens in a project

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp list-screens \
  --project-id "4044680601076201931"
```

### 5. Get a specific screen

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp get-screen \
  --name "projects/4044680601076201931/screens/98b50e2ddc9943efb387052637738f61" \
  --project-id "4044680601076201931" \
  --screen-id "98b50e2ddc9943efb387052637738f61"
```

### 6. Edit existing screens

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp edit-screens \
  --project-id "4044680601076201931" \
  --selected-screen-ids '["98b50e2ddc9943efb387052637738f61"]' \
  --prompt "Change the button color to blue and increase the font size of the title"
```

To edit multiple screens at once, include all screen IDs in the JSON array:
```bash
--selected-screen-ids '["screen_id_1", "screen_id_2"]'
```

### 7. Generate design variants

Generate multiple design alternatives from an existing screen:

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp generate-variants \
  --project-id "4044680601076201931" \
  --selected-screen-ids '["98b50e2ddc9943efb387052637738f61"]' \
  --prompt "Create variants with different color schemes" \
  --variant-options '{"variantCount": 3, "creativeRange": "EXPLORE", "aspects": ["COLOR_SCHEME"]}'
```

**`--variant-options` fields**:
- `variantCount`: Number of variants to generate (1–5, default 3)
- `creativeRange`: `REFINE` (subtle), `EXPLORE` (balanced, default), `REIMAGINE` (radical)
- `aspects`: Which aspects to vary — `LAYOUT`, `COLOR_SCHEME`, `IMAGES`, `TEXT_FONT`, `TEXT_CONTENT`

### 8. Get a specific project

```bash
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp get-project \
  --name "projects/4044680601076201931"
```

## End-to-End Example

Design a new mobile app onboarding flow:

```bash
# 1. Create project
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp create-project --title "Onboarding Flow"

# 2. Generate the welcome screen (note the project ID from step 1)
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp generate-screen-from-text \
  --project-id "PROJECT_ID" \
  --prompt "Welcome screen for a travel app. Shows a hero image of a mountain, app name 'Voya', tagline 'Your journey starts here', and a Get Started button" \
  --device-type MOBILE

# 3. List screens to get the screen ID
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp list-screens --project-id "PROJECT_ID"

# 4. Generate color scheme variants of the welcome screen
uvx mcp2cli --mcp https://stitch.googleapis.com/mcp generate-variants \
  --project-id "PROJECT_ID" \
  --selected-screen-ids '["SCREEN_ID"]' \
  --prompt "Explore different color palettes" \
  --variant-options '{"variantCount": 3, "creativeRange": "EXPLORE", "aspects": ["COLOR_SCHEME"]}'
```

## Tips

- **Project ID vs resource name**: Commands like `list-screens`, `generate-screen-from-text`, `edit-screens`, and `generate-variants` take `--project-id` (bare ID only). Commands like `get-project` and `get-screen` take `--name` (full resource path).
- **Generation is async**: If a generation call times out, use `get-screen` to retrieve the result later.
- **Inspect any command**: Run `<command> --help` for full parameter details.
  ```bash
  uvx mcp2cli --mcp https://stitch.googleapis.com/mcp generate-variants --help
  ```
