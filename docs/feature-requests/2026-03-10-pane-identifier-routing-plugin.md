# Feature Request: Pane Identifier Routing Plugin for Silicato Operator

Date: 2026-03-10
Status: Proposed
Owner: OG (requested), Sil (drafted)

## Summary

Add a routing plugin/feature to Silicato Operator so users can target tmux panes by **stable human-readable identifiers** instead of raw tmux targets.

Example intent:
- Spawn silicato session(s)
- Assign identifiers to panes (e.g., `gaia`, `soil`, `profile`, `ls1up`)
- Inject transcript/prompt by identifier

## Problem

Current workflows require direct tmux target references (`session:window.pane`), which are brittle and hard to remember in multi-pane setups.

Pain points:
- Manual pane lookup overhead
- Frequent target mistakes
- Reduced speed in multi-agent/multi-pane operation

## Proposed Solution

Introduce a local routing registry:

`identifier -> tmux_target`

with CLI commands for route management and prompt injection.

## CLI Proposal (MVP)

### Route management

```bash
silicato route add <id> <tmux_target>
silicato route list
silicato route remove <id>
silicato route update <id> <tmux_target>
```

### Injection by identifier

```bash
silicato inject --to <id> --text "..."
silicato inject --to <id> --from-file ./transcript.txt
```

Optional quality-of-life:

```bash
silicato route resolve <id>   # print tmux target
silicato route check <id>     # validate target exists/alive
```

## Data Model

Persist routes in local config (user scope), e.g.:

`~/.config/silicato/routes.json`

Schema (example):

```json
{
  "routes": {
    "gaia": {
      "tmuxTarget": "dev:0.1",
      "updatedAt": "2026-03-10T17:00:00Z"
    },
    "soil": {
      "tmuxTarget": "farm:1.0",
      "updatedAt": "2026-03-10T17:02:00Z"
    }
  }
}
```

## UX / Safety Rules

1. Validate route exists before injection.
2. Validate tmux target exists/is alive before send.
3. If stale route detected, return actionable error + rebind hint.
4. ID collisions should require explicit `--force` for overwrite.
5. Identifier format should be constrained (e.g. `[a-z0-9_-]+`).

## Non-Goals (MVP)

- Complex orchestration logic
- Auto-discovery/auto-healing of routes
- Networked shared route registries

## Acceptance Criteria

1. User can bind a pane to an identifier and list bindings.
2. User can inject text to pane by identifier without referencing raw tmux target.
3. Stale/dead pane routes fail safely with clear recovery message.
4. Routes persist across process restarts.
5. Unit tests cover route CRUD + inject error cases.

## Why This Matters

This improves operator ergonomics and reduces routing friction for multi-pane agent workflows.
It aligns with fast local iteration and reliable multi-agent execution patterns.
