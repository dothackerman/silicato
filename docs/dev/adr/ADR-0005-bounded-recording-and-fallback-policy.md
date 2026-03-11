# ADR-0005 Bounded Recording and Fallback Policy

Status: Superseded by ADR-0006
Date: 2026-03-11

## Context

Silence-based auto-stop can fail in realistic environments:
- persistent ambient noise can prevent silence detection
- threshold misconfiguration can keep speech state "active" indefinitely
- device/runtime glitches can keep a turn open longer than intended

Unbounded recording creates operational risk in a terminal-first workflow:
- hangs delay turn completion
- resource use increases for both capture and transcription
- operator feedback becomes unpredictable

Silicato already introduced deterministic max-duration fallback behavior in the
auto-stop design and business rules. The missing piece was an explicit ADR that
documents why the policy exists and how operators can control it.

## Decision

1. Recording remains bounded by a deterministic max-duration fallback.
2. The fallback is configurable via CLI (`--max-recording-seconds`).
3. Default fallback value is `120s`.
4. `0` is allowed to disable the hard-stop fallback for advanced users.
5. Silence stop and max-duration are independent controls; either can be tuned
   or disabled by operator intent.

## Consequences

Positive:
- prevents indefinite hangs when silence detection never triggers
- keeps behavior deterministic and testable
- provides explicit operator control over long-form dictation vs. guardrails

Negative / tradeoffs:
- too-low max values can truncate long turns
- disabling both silence stop and max-duration can reintroduce unbounded
  recording risk

## Alternatives considered

1. No max-duration fallback (fully unbounded recording)
- Rejected: unacceptable hang risk and non-deterministic UX under noise/misconfig.

2. Fixed hardcoded max with no CLI control
- Rejected: inflexible across short-command and long-dictation workflows.

3. Adapter-only timeout policy without domain ownership
- Rejected: weak replayability and poor parity between live runtime and offline
  evaluation.
