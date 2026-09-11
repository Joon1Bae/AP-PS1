---
name: TP
description: Traceable Prompt — REQUIRED before every substantive AI request on this problem set (BUSFIN 8200 AI policy). Snapshots the repo, does the work within policy limits, appends an AI_INTERACTIONS.md entry, snapshots again.
---

# /TP — Traceable Prompt

Purpose: create a contemporaneous, auditable record of AI use, as required by the BUSFIN 8200
problem set AI policy. Follow every step in order. If any step fails (a commit does not get
created, the entry cannot be appended), **stop and fix the record before continuing**.

The user's substantive request is given as the skill argument, or in the message that invokes
`/TP`. If no request is given, ask for it.

## Step 1 — Identify the problem set item
Determine which problem set item (question / sub-item, e.g. "Q2(b)") the request concerns.
If it is not clear from the request, the open files, or the conversation, **ask the user to
specify the item before doing any substantive work**.

## Step 2 — Snapshot BEFORE
Run, from the repository root:
```
git add -A
git commit -m "TP before: <item> - <short description of request>" --allow-empty
git rev-parse HEAD
```
Record the resulting commit hash as `before_hash`. If there were no file changes, the
`--allow-empty` flag still records the state. Do not skip this even if the last commit is recent.

## Step 3 — Do the substantive work, within the course AI policy
Apply the rules in `CLAUDE.md`:
- **Math**: only check a completed derivation or diagnose a specific step of a partial one.
  Explain *why* a step is wrong; do not rewrite, complete, or continue the derivation.
- **Economic reasoning**: only critique an answer the student has already written; do not
  generate, rewrite, or edit the reasoning.
- **Data analysis**: implement the student's specification. If the implementation requires a
  substantive mathematical, economic, or econometric decision not covered by the spec
  (sample restriction, timing convention, missing data, variable definition, winsorization,
  regression specification, standard errors, ...), **identify the ambiguity and ask the user
  to decide before implementing**. Record both the ambiguity and the user's decision.
- Formatting / translation / LaTeX help is allowed once the substantive content exists, and is
  labeled as such in the entry.

Keep track, as you work, of: files inspected, files modified, errors/omissions/ambiguities
identified, and any substantive suggestions you made (even ones the student did not adopt).

## Step 4 — Append the entry to AI_INTERACTIONS.md
Append (never modify, delete, combine, or rewrite earlier entries) a new entry at the **end** of
`AI_INTERACTIONS.md`, numbered sequentially, using exactly this template:

```
## Interaction N — <item> — <YYYY-MM-DD HH:MM>

- **Problem set item:** <e.g. Q2(b)>
- **Substantive prompt (verbatim):** <the user's request, quoted verbatim; keep original language>
- **Purpose:** <one or two sentences>
- **Git commit before:** <before_hash>
- **Assistance provided:** <concise but complete description of what was done>
- **Files inspected:** <list>
- **Files directly modified by AI:** <list, or "none">
- **Errors, omissions, or ambiguities identified:** <list, or "none">
- **Substantive mathematical / economic / empirical suggestions made:** <list, or "none">
- **Type of assistance:** <all that apply: math review; economic reasoning review; empirical
  implementation; code debugging; formatting/translation; other (specify)>
- **Grouped follow-up requests:** <"none", or a list of the minor debugging/formatting follow-ups
  on the same item in this session that were grouped into this entry, each with a short
  description>
- **Git commit after:** <after_hash, filled in Step 5>
```

If `AI_INTERACTIONS.md` does not exist, create it with the header
`# AI_INTERACTIONS.md — BUSFIN 8200 Problem Set 1` and a one-line note that entries are
append-only, then add the entry.

## Step 5 — Snapshot AFTER
```
git add -A
git commit -m "TP after: <item> - <short description>" --allow-empty
git rev-parse HEAD
```
Record the hash as `after_hash`. Then write `after_hash` into the entry's
"Git commit after" line and amend nothing — instead make one more small commit:
```
git add AI_INTERACTIONS.md
git commit -m "TP record: <item> - after hash"
```
(Two commits after the work is acceptable; the "after" snapshot hash is what the entry cites.)

## Step 6 — Grouping follow-ups
If, in the same session, the user asks minor follow-up debugging or formatting requests on the
**same item** and explicitly says to group them, add them to the "Grouped follow-up requests"
line of the current entry and make a new "TP after" commit at the end of the group. Only group
when all three hold: same item, same session, documented together. A new item or a new
substantive request always starts a new `/TP` cycle.

## Report to the user
Finish by telling the user (in Korean): the item, `before_hash`, `after_hash`, the entry number,
and any ambiguities that still need their decision.

This skill helps create an auditable record. It does not weaken or replace any requirement of
the course AI policy.
