# Operating Constraints of an LLM Agent in a Multi-Repository Project

**Field**: *Context Engineering* (Mei et al., 2025, arXiv:2507.13334) and *LLMOps* — the discipline governing what information, in what form, reaches a language model at inference time. This is not data science (statistical inference over a dataset): here the "data" is the agent's own operating context — instructions, memory, token budget — not an external corpus under analysis.

---

## 1. Context bootstrap (fixed trigger rule)

In the Context Engineering literature, *context management* — what persists, what is dropped, what is reloaded — is recognized as one of the field's foundational components alongside retrieval, generation, and processing (Mei et al., 2025). An agent does not automatically retain a set of behavioral constraints for a session's full duration: a rule file existing on disk is not the same as its content having actually been loaded into the model's active context.

**Trigger rule**: at the start of every new session, **and** after every conversation compaction (`/compact` — the operator that summarizes a long exchange to free context window space), the agent must explicitly reload its operating rule module (`session-rules`) before taking any other action.

The two trigger events are not distinct cases — they are the same failure condition (loss of, or absence of, a fully-loaded rule context) reached by two different paths. A compaction preserves a reference to a rule's existence, not its literal content; a fresh session simply never passes through the event that would trigger reloading, if that event is not also defined explicitly for session start.

**Project-specific constraint**: every technical conclusion must pass through the local retrieval-augmented generation system (this repository) before being written — no unverifiable assertion against the indexed sources. The process is traced explicitly: which queries were run, what they returned, why a given implementation choice followed from it.

**Budget constraint**: each session operates under a finite token budget (on the order of one million) and no implicit memory of a previous session's failed attempts on the same project. This implies a direct operating principle: every action should be targeted, not exploratory — abstract reasoning is resolved at the planning stage, leaving execution a narrow, mechanical path. A wasted operation is not merely an isolated cost: it is budget taken from a later, better-aimed attempt. Wu et al. (2026) formalize the same principle for long-horizon search agents as a sequential decision problem constrained by an explicit context budget (the BACM framework), reporting gains of over 1.6x versus unconstrained baselines precisely from choosing selectively *when* to compress, rather than compressing uniformly.

---

## 2. Codified operating rules (the `session-rules` module)

Full content of the module reloaded at bootstrap, not a summary of it.

### 2.1 Token-budget discipline

| # | Constraint |
|---|---|
| 1 | Never have the agent generate content that already exists on disk as a tool call's parameter (e.g. a publish payload to a remote repository). Content passed as a parameter is generated output — it costs as much as, or more than, rewriting the file from scratch. Read it directly from the filesystem instead. |
| 2 | For publishing to a Git repository: prefer local operations (`add`/`commit`/`push`, zero generation cost) over API calls that require the whole file as a string in the request. Programmatic interfaces are reserved for read/metadata operations (branches, pull requests, status). |
| 3 | Don't re-read a file already read or written earlier in the same session — its content is still in the active context. |
| 4 | Targeted diff, not full rewrite, when modifying an existing file. |
| 5 | Batch independent tool calls into a single turn rather than sequencing them. |
| 6 | Avoid unnecessary sub-agent chains for direct tasks: each sub-agent initializes a cold context, at a full, separate cost. |
| 7 | Don't re-run an entire verification suite when a targeted subset validates the single change introduced. |
| 8 | Terse replies: no redundant recap of output already visible to the user. |
| 9 | **Energy-priority principle**: token cost is a billing matter; the underlying compute is real electricity, with a real environmental cost, independent of who bears the economic cost. Verify feasibility and scale before launching an expensive computation — never blind. |

### 2.2 Technical documentation conventions (project-specific, Dense-Evolution)

Sixteen numbered rules requiring: a progressive-guide structure (not a pure API reference); conceptual ground-zero before showing code; incrementally-built numbered steps; self-contained code blocks; no inline comments (explanations live in prose); short variable naming; a single canonical solution per step, with alternatives confined to a closing section; real functions invoked directly, never behind opaque wrappers; bug provenance and history isolated to a closing "Details" section; no self-referential narration by the agent within the guide; every reported numeric value must have been executed and verified, never estimated.

---

## 3. Cross-session persistent memory

An accumulated observation store (roughly 35 entries at time of writing), consulted for contextual relevance rather than reloaded in full every turn — a two-tier memory architecture (working context vs. long-term store) consistent with what is described for long-horizon agent systems in the Context Engineering literature. Representative entries:

- Token-economy discipline, as a cross-cutting operating principle.
- Verification of a published artifact via actual browser loading, never from source code alone.
- Prohibition on delegating literature research to sub-agents when direct action is available.
- Prohibition on isolation in parallel working environments (worktrees) absent an explicit request.
- Mandatory serialization of heavy computational loads, never run in parallel without warning.
- Rules of engagement for security testing: demonstrate a vulnerability, never exploit it.
- Scope verification before any structural promotion of a module (code, tests, continuous integration, documentation), to avoid duplicating existing work.

---

## 4. Baseline behavioral constraints

Independent of the specific project:

- No feature or abstraction beyond what the task requires.
- No error handling for cases that cannot occur.
- Code comments only for non-obvious rationale, never descriptive of the obvious.
- Explicit confirmation required before an irreversible or high-impact action (force-push, deletion, external publication), absent specific prior authorization.
- Version-control state verification before commands that could discard unsaved work.
- No bypassing a safety check instead of resolving its underlying cause.

---

## 5. Tool-specific constraints (conditional activation)

Not a fixed, known-in-advance list: each integration (version control, a publishing surface, a documentation-lookup service) introduces its own operating conventions, active only for the duration of the turn in which that tool is actually invoked — a direct instance of the "just-in-time context" principle described in Mei et al. (2025) for external tool integration in an agentic architecture.

---

## Closing methodological note

None of these levels is kept active by repeated re-reading every turn. Levels 1, 2, and 4 persist in context once loaded; level 3 is queried for relevance; level 5 activates only on actual use of the corresponding tool. Over a long or thematically heterogeneous session, one level can be applied correctly while another is missed — precisely the condition the bootstrap rule (Section 1) was revised to cover fully.

## References

1. L. Mei et al., *A Survey of Context Engineering for Large Language Models*, arXiv:2507.13334 (2025).
2. Y. Wu et al., *ContextBudget: Budget-Aware Context Management for Long-Horizon Search Agents*, arXiv:2604.01664 (2026).
