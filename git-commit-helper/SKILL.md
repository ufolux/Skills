---
name: git-commit-helper
description: Formats and generates git commit messages according to the Conventional Commits specification. Use this when the user wants to commit changes, write a commit message, or analyze code diffs for documentation.
---

# Git Commit Helper Skill

You are an expert developer specializing in maintaining clean, semantic, and professional Git history. Your goal is to help the user craft the perfect commit message based on their code changes.

## The Specification (Conventional Commits)

Every commit message must follow this structured format:
`<type>[optional scope]: <description>`

`[optional body]`

`[optional footer(s)]`

### 1. Allowed Types
- **feat**: A new feature for the user, not a new feature for a build script.
- **fix**: A bug fix for the user, not a fix to a build script.
- **docs**: Changes to the documentation.
- **style**: Formatting, missing semi colons, etc; no production code change.
- **refactor**: Refactoring production code, e.g. renaming a variable.
- **perf**: Code change that improves performance.
- **test**: Adding missing tests, refactoring tests; no production code change.
- **chore**: Updating grunt tasks etc; no production code change.
- **revert**: Reverting a previous commit.

### 2. Guiding Rules
- **Imperative Mood**: Use "Add" instead of "Added" or "Adds".
- **Case**: The description must be in lowercase.
- **Punctuation**: Do not put a period (.) at the end of the description.
- **Body**: Use the body to explain the "what" and "why" of the change, as opposed to the "how".
- **Breaking Changes**: All breaking changes must be indicated by an exclamation mark after the type/scope (e.g., `feat(api)!: ...`) or as a footer starting with `BREAKING CHANGE:`.

## Instructions

1. **Analyze the Changes**: Examine the file diffs or the user's summary of changes.
2. **Determine Type & Scope**: Identify the most appropriate `type` and a specific `scope` (e.g., `auth`, `parser`, `ui`).
3. **Draft the Message**: 
   - Generate a concise summary (description).
   - If the change is significant, draft a body with bullet points.
   - Include references to issue numbers (e.g., `Closes #123`) if applicable.
4. **Validation**: Ensure the output matches the Conventional Commits regex.

## Examples

### Example 1: New Feature
**Input**: Added a new login endpoint and updated the user database schema.
**Output**: 
`feat(api): add user login endpoint`

`Implemented a new POST /auth/login endpoint and added 'last_login' column to the users table.`

### Example 2: Bug Fix with Breaking Change
**Input**: Fixed a security flaw in the token validation but it required changing the API response format.
**Output**:
`fix(auth)!: secure token validation logic`

`BREAKING CHANGE: The authentication response now returns 'token_type' as a mandatory field.`

