---
name: voyagely-agentic-e2e
description: Use this skill whenever the user asks an AI agent to improve the Voyagely iOS app autonomously, run an agentic E2E loop, explore the live app with Maestro, create or triage candidates, promote OpenSpec changes, implement fixes, verify with Swift tests and Maestro flows, or build a repeatable self-improving workflow. This skill is specifically for Codex/OpenSpec/Maestro-driven product discovery, implementation, and regression in the VoyaProject repo.
---

# Voyagely Agentic E2E Workflow

This skill guides an AI agent through Voyagely's self-improving development loop: observe the running app, discover candidates, specify changes, implement safely, verify with Swift tests and Maestro flows, and feed lessons back into the queue.

Use this skill in `/Users/richard/Code/github_projects/VoyaProject`.

## Start Here

Read these files before acting:

1. `AGENT.md` for project rules and hard gates.
2. `docs/DEVELOPMENT_SETUP.md` for local tool setup.
3. `agentic-e2e/README.md` and `agentic-e2e/candidate-flow.md` for workflow semantics.
4. Relevant candidate/OpenSpec files:
   - `agentic-e2e/inbox/<candidate-id>/candidate.json`
   - `openspec/changes/<change-id>/proposal.md`
   - `openspec/changes/<change-id>/design.md`
   - `openspec/changes/<change-id>/tasks.md`
   - `openspec/changes/<change-id>/acceptance.yaml`

Before doing work, check:

```bash
git status --short
node --check agentic-e2e/runner/run.mjs
node agentic-e2e/runner/run.mjs --dry-run
```

If the user interrupted an automation run, check for stale processes and stop only the stale child processes from that run:

```bash
ps -eo pid,ppid,command | rg "agentic-e2e/runner/run.mjs|codex exec --cd .*/VoyaProject" || true
```

## Context Management

When the active context reaches 85%, run a context compact before continuing. Do this proactively to avoid context-window related mistakes during long agentic loops.

## The Loop

Run the workflow as a budgeted loop, not an unbounded background job.

1. **Explore**
   - Read PRD, UserJourneys, OpenSpec, code, and prior candidates.
   - Use Maestro to drive live simulator UI when the task is about UI behavior, navigation, visual review, bug reproduction, or E2E confidence.
   - Use AXe only for accessibility tree or selector diagnosis.

2. **Candidate**
   - Write findings to `agentic-e2e/inbox/<candidate-id>/candidate.json`.
   - Use the schema in `agentic-e2e/schemas/candidate.schema.json`.
   - Include evidence from PRD/OpenSpec/code/Maestro failures/screenshots/videos, AXe traces, or Swift test failures.

3. **Validate**
   - Run the runner for mechanical checks:

```bash
node agentic-e2e/runner/run.mjs --max-cycles 1
```

4. **Specify**
   - Promote validated candidates into OpenSpec changes only when gates allow.
   - Validate OpenSpec strictly:

```bash
openspec validate <change-id> --strict
```

5. **Implement**
   - Implement from `tasks.md`.
   - Keep edits scoped.
   - If a task requires a product decision not present in the spec, stop and create a clarification file instead of guessing.

6. **Verify**
   - Run the smallest relevant tests first.
   - For non-UI logic, prefer focused XCTest / Swift Testing.
   - For UI/E2E behavior, run Maestro flows.
   - For accessibility or selector drift, capture AXe evidence only when needed.

7. **Retrospective**
   - Record reusable lessons in the change retrospective or as follow-up candidates.
   - Do not bury important failures in free-form chat only.

## Tool Split

Use the right execution layer for the job:

| Need | Tool | Why |
| --- | --- | --- |
| Non-UI business/data logic | XCTest / Swift Testing | Fast, direct assertions without launching UI. |
| UI/E2E user journey | Maestro CLI | Unified black-box flows that can migrate across platforms. |
| UI walkthrough / visual review | Maestro screenshot/video + Codex CLI | Maestro preserves evidence; Codex reviews visual quality. |
| Bug reproduction | Maestro CLI | Flow failure screenshots/videos reduce manual reproduction. |
| Accessibility/selector diagnosis | AXe | Direct accessibility tree inspection; not the main E2E layer. |

Do not add new XCUITest coverage for UI/E2E journeys. Existing XCUITest can stay as a migration safety net until equivalent Maestro smoke/regression flows are stable.

## Maestro UI/E2E

Verify tools:

```bash
mkdir -p ~/.maestro
command -v maestro
MAESTRO_CLI_NO_ANALYTICS=1 maestro --version
MAESTRO_CLI_NO_ANALYTICS=1 maestro test --help
```

Run a flow:

```bash
MAESTRO_CLI_NO_ANALYTICS=1 maestro test \
  -e APP_ID=com.itchscratch.voyagely \
  agentic-e2e/maestro/flows/smoke/launch.yaml
```

Maestro flow contract:

```yaml
appId: ${APP_ID}
---
- launchApp:
    clearState: true
    clearKeychain: true
    arguments:
      UITEST_RESET_STATE: true
      UITEST_DISABLE_DEBUG_TOOLS: true
      UITEST_DISABLE_ANIMATIONS: true
      UITEST_USE_MOCK_DATA: true
- assertVisible:
    id: "auth.login.email_field"
```

Use Maestro artifacts as candidate evidence:

```json
{
  "type": "maestro_failure",
  "ref": "agentic-e2e/maestro/artifacts/<flow-run>/failure.log",
  "notes": "The expected screen did not appear after the user journey flow."
}
```

## Candidate Types

Use these classifications consistently:

- `defect`: implemented UI or behavior violates PRD/OpenSpec/UserJourney.
- `test_gap`: behavior exists but lacks executable regression coverage.
- `testability_gap`: behavior cannot be tested reliably because selectors, fixtures, or oracles are missing.
- `clarification`: product semantics conflict or are not safe to infer.
- `requirement`: a new product behavior backed by strong evidence. Keep it behind human triage.

Confidence should be semi-mechanical. Prefer evidence-backed scoring from `agentic-e2e/candidate-flow.md` over LLM self-confidence.

## Human Gates

Do not cross these gates automatically:

- New requirement promotion.
- Unresolved clarification.
- Scope-creep meta-candidate.
- Selector baseline update.
- Production-like verification.
- Merge, push, or PR creation.
- Auth semantics, destructive data flows, production config, data migrations, or sync conflict behavior.

If blocked, write down the blocker in the candidate, OpenSpec clarification, or runner report. Do not silently proceed.

## Implementation Policy

Automatic implementation is allowed only when all are true:

- Candidate is validated.
- Classification is `defect`, `test_gap`, or `testability_gap`.
- Risk is low.
- OpenSpec change exists and passes strict validation.
- Verification strategy uses Swift tests for non-UI logic and Maestro flows for UI/E2E paths.
- The worktree state has been checked and unrelated user changes will not be overwritten.

For implementation:

```bash
openspec validate <change-id> --strict
```

Then implement tasks from:

```text
openspec/changes/<change-id>/tasks.md
```

If implementation reveals ambiguity, create:

```text
openspec/changes/<change-id>/clarifications/<clarification-id>.json
```

and stop that change until resolved.

## Accessibility Contract

Durable Maestro E2E flows should use stable identifiers, not labels, copy, hierarchy indexes, or coordinates.

- Central namespace: `Voya/Voya/Utilities/AccessibilityIdentifiers.swift`
- SwiftUI usage: `.accessibilityIdentifier(...)`
- Naming convention: `<feature>.<screen>.<element>`
- Use deterministic suffixes for repeated domain items.
- If Maestro cannot target a normal control by identifier, create a `testability_gap` candidate.
- If AXe shows missing or unstable identifiers, use it as diagnostic evidence for that candidate.

Coordinates are acceptable only for map/spatial interactions or temporary exploration. Do not make coordinate taps the durable oracle for normal controls.

## Verification Commands

Build:

```bash
xcodebuild build \
  -project Voya/Voya.xcodeproj \
  -scheme Voyagely \
  -destination 'platform=iOS Simulator,name=iPhone 16,OS=18.6'
```

Non-UI Swift test:

```bash
xcodebuild test \
  -project Voya/Voya.xcodeproj \
  -scheme Voyagely \
  -destination 'platform=iOS Simulator,name=iPhone 16,OS=18.6' \
  -only-testing:VoyaTests
```

Maestro UI/E2E smoke:

```bash
MAESTRO_CLI_NO_ANALYTICS=1 maestro test \
  -e APP_ID=com.itchscratch.voyagely \
  agentic-e2e/maestro/flows/smoke/launch.yaml
```

Agentic runner:

```bash
node agentic-e2e/runner/run.mjs --dry-run
node agentic-e2e/runner/run.mjs --max-cycles 10
node agentic-e2e/runner/run.mjs --execute --max-cycles 1
```

Use `--execute` sparingly. It may call external Codex CLI and consume quota.

## Failure Handling

If Maestro fails during initialization with `~/.maestro/analytics.json` missing, create `~/.maestro` and rerun with `MAESTRO_CLI_NO_ANALYTICS=1`.

If Maestro or `simctl` fails with CoreSimulator permission errors, rerun with the user's approved external permission path. Record the failure as environment evidence if it blocks verification.

If Codex CLI fails because it cannot access `~/.codex/sessions` or the network, treat it as an environment failure, preserve the runner artifact, and retry only when an external execution path is available.

If Xcode tests fail, do not broaden the change immediately. First identify whether the failure is:

- app behavior,
- fixture setup,
- selector mismatch,
- simulator/environment issue,
- spec ambiguity.

Then either fix the scoped issue, create a follow-up candidate, or write a clarification request.

If Maestro flow fails, preserve screenshots/videos/logs under `agentic-e2e/maestro/artifacts/`, classify the failure, and create a follow-up candidate when it is not part of the current acceptance.

## Output Shape

When reporting back to the user, include:

- what loop stage ran,
- candidate/change ids touched,
- files created or modified,
- verification commands and results,
- blockers or human gates,
- next recommended work item.

Keep the report short enough to act on.
