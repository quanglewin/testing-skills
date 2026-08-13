---
name: improve-skill
description: "Repo-internal: run the eval harness, diagnose failures, and propose rule-file improvements as a reviewable branch/PR. Use when asked to improve, tune, or auto-improve the test-generation skills. Never auto-merges. Not for installation into user projects."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion
---

# Improve Test-Generation Skills

You will run the evaluation harness, diagnose why the `generate-tests` skill under-performs,
apply minimal rule-file edits, verify they help, and package the result as a reviewable PR.
This loop **never merges anything** — CODEOWNER review gates every change.

**Scope:** $ARGUMENTS (default: all ecosystems; may name one, e.g. `csharp` or `typescript`)

## Loop (max 3 iterations)

### 1. Baseline

Invoke the `eval-skills` skill for the scoped ecosystem(s). If everything passes all gates,
report "no improvement needed" with the scorecard and stop — do not invent changes.

### 2. Classify every failure

For each failed dimension / missed case / violation, assign exactly one class:

| Class | Meaning | Action |
|---|---|---|
| RULE_MISSING | No rule covers the failing behavior | Draft a new rule section or file |
| RULE_AMBIGUOUS | A rule exists but is vague enough that a reasonable reading produces the failure | Clarify wording, add an Incorrect/Correct pair showing the exact failure |
| RULE_IGNORED | The rule is clear; the generation run didn't follow it | Strengthen the rule's prominence (FORBIDDEN section, checklist entry) or the SKILL.md step that loads it |
| FIXTURE_BUG | The fixture or golden list is wrong (e.g. golden case for a branch that doesn't exist) | Report only — do NOT fix silently; list under "Needs human decision" |
| EVAL_BUG | The rubric/grep misfired (false positive) | Report only — same as above |

Cite evidence for every classification: the failing output, the rule text (or its absence),
the fixture line.

### 3. Edit (RULE_* classes only)

- Minimal diffs: a new Incorrect/Correct pair, a clarified sentence, a new FORBIDDEN entry — not rewrites.
- If a **general** rule changes, apply the identical change to BOTH copies (`skills/generate-test-cases/rules/general/` and `skills/generate-tests/rules/tests/general/`) in the same commit.
- If a new rule file is created, add it to the Rules Reference in the relevant SKILL.md file(s).
- Never touch fixture production code or golden lists to make results look better.

### 4. Re-verify

Re-run `eval-skills` for the affected ecosystem.
- Score improved and no dimension regressed → keep the edits.
- Otherwise → revert them (`git checkout -- <files>`) and record why the hypothesis failed.

### 5. Iterate or stop

Stop when: all gates pass, OR 3 iterations done, OR remaining failures are all FIXTURE_BUG/EVAL_BUG.

## Packaging

Work on a branch `improve-skill/{date}-{ecosystem}` off the current branch (never commit to `main`).
Commit kept edits with messages explaining the failure each edit addresses. Then produce a PR
body (use `gh pr create` only if the user confirms pushing) containing:

- Before/after scorecard table per ecosystem
- Per-edit rationale: failure → classification → edit → re-eval delta
- "Needs human decision" section: all FIXTURE_BUG / EVAL_BUG findings
- Reminder line: general-rule copies synced (or "no general rules touched")

If the user has not asked to push, stop after committing locally and show the PR body draft.

## Boundaries

- **Never** merge, never push without explicit confirmation, never edit `main` directly.
- **Never** modify fixture `src/` or `expected-cases.md` to improve scores (report suspected fixture bugs instead).
- **Never** weaken the rubric (`harness/rubric.md`) to make a run pass — rubric changes are "ask first" per the spec.
- Keep the two general-rules directories byte-identical at every commit.
