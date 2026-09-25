# Two Further Workflows: Building a Discovery Repository and an Evolving Software Repository

**Nature of this document**: a companion to [`draft_verification_methodology.md`](draft_verification_methodology.md), same status — a **process** document describing how a human researcher structures work, not an instruction addressed to an AI. That document covers workflows 1 and 2 (Brainstorming, Coding). This page covers workflows 3 and 4: how to structure the two repositories that a brainstormed, coded result eventually lands in — a **Discovery** repository (where a result is tested and may be rejected) and an **Evolving Software** repository (where only what survives Discovery ships to real users).

---

## Workflow 3 — Building a Discovery Repository

**Purpose**: a place to run an idea against reality before it is allowed to affect anything real. Not a staging area for code that is already believed correct — a place where being wrong is the expected, normal outcome of most entries, and is recorded exactly as carefully as being right.

**Structural rules**:

1. **One script per idea, runnable standalone.** Every entry is a single script that produces its own result end to end — never a module other entries import from. This keeps ideas independent: a later finding can contradict an earlier one without any code needing to change.
2. **A test mirrors a script only when the script's own claim needs re-checking automatically.** Not every entry needs one — an exploratory script that already recorded its one-time result in its write-up does not need to be re-run forever; a script whose claim later gets relied on elsewhere does.
3. **No publishing gate.** Version freely, one bump per entry recorded, independent of any package index. The cost of being wrong here is a documented negative result, not a broken release.
4. **A negative result is written up with the same care as a positive one**, and is not deleted or hidden once found to be wrong — it is marked as resolved and left in place, so the next attempt (human or AI) does not repeat it. The single most common way a promising-looking result turns out to be wrong: check it against a **negative control** — rerun the exact same analysis on data known to contain no real effect (shuffled order, a randomized label, a mismatched baseline) — and see whether the "effect" survives. If it appears identically in both, it was never a real effect.
5. **Promotion out of Discovery is deliberate and one-directional.** A result moves into the Evolving Software repository only after being independently re-verified — never automatically, never because it merely exists here.

**Failure mode this workflow exists to prevent**: treating a first promising result as if it were already a finding, and shipping it before anyone checked whether it survives being questioned.

---

## Workflow 4 — Building an Evolving Software Repository

**Purpose**: the repository real users install. Only what a Discovery repository's negative controls did not kill reaches this point — and the standard of care here is higher, not equal, because a mistake here reaches people who were never part of the process that produced it.

**Structural rules**:

1. **The list of what actually ships must be kept honest.** Any packaging configuration that names distributable components by hand (rather than discovering them automatically) is a list that *will* drift the moment a new component is added and the list is not updated in the same commit — a real, recurring failure mode, not a hypothetical one: a component can pass every local test (tests run against the source tree directly) while being silently absent from what actually gets built and shipped, and the gap is only found once an independent installer hits a real import error. Check the shipped list against the real directory tree as part of building every release, not only when something breaks.
2. **A release is never manually declared correct — the platform enforces it structurally.** Configure the hosting platform so that merging to the branch users build against is physically refused until a named set of checks reports success. This is not a courtesy; it is the difference between "nobody remembered to check" and "it is not possible to skip checking."
3. **Publishing to a package index is a distinct, separate, human-confirmed step from everything before it — never automated away.** Build the distributable artifact, verify its metadata independently of the build step that produced it, and only *after* a human confirms the upload actually succeeded does the repository's own permanent record (a version tag, a public release note) get created. A tag or release created before that confirmation can end up pointing at something that was never actually published, or at a version number that had to be abandoned after publishing failed partway.
4. **Versioning communicates what changed, honestly.** New capability that does not break anything existing is a different kind of change from a same-behavior fix — pick the version-number position that matches which one actually happened, not whichever feels more exciting.
5. **A red status check is not a single category.** Before reacting, determine which of three things actually happened: a real defect in the change (fix at the root, not by rerunning); already-documented infrastructure noise unrelated to the change (confirmed by reading the actual failure, not assumed — then safe to simply retry); or a defect the test suite itself cannot see at all (rule 1 above is the standing example — caught only by a real, independent consumer actually installing the real artifact, never by the suite that built it).

**Failure mode this workflow exists to prevent**: confusing "every test passed" with "this is safe to give to someone else" — a coverage number, a green checkmark, and a successful build are each evidence toward that conclusion, not proof of it individually or together.
