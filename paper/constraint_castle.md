# A Four-Layer Architecture for AI-Assisted Research: Exploration, Verification, Discovery, Production

## Abstract

This paper is an experience report, not a controlled study. It describes a four-layer architecture for organizing AI-assisted research work, developed empirically over the course of a real project and compared against existing literature only after the fact. The four layers — Exploration, Verification, Discovery, Production — are not interchangeable: each has its own environment, its own success criterion, its own controls, and its own model requirements. The documentation of the architecture is deliberately asymmetric: Layer 1 (Exploration) is a predominantly conversational, lightweight phase that requires no dedicated process document; Layers 2–4 are convergent, verifiable, and therefore documented. Within Layer 2 (Verification) we report a concrete failure mode — the *reload gap* — in which a standing behavioral constraint for an LLM coding agent was written correctly but scoped to only one of two functionally identical trigger events. The fix required no new mechanism, only the widening of an existing trigger condition to match the actual failure surface. We argue that model names are part of the method, not interchangeable components: each layer assumes capabilities (context window size, tool integration, agentic behavior) that differ across models and determine what the layer can do. We close with the distinction between process documents (addressed to the human researcher) and constraint documents (addressed to the AI), which we did not find explicitly formulated in the literature we surveyed.

---

## 1. Introduction

How does a human researcher structure work carried out jointly with several different AI systems, so that the result is reproducible, verifiable, and stable? The question is not new, but most existing answers are either *model-agnostic* (frameworks that assume any sufficiently capable LLM will do) or *single-phase* (how to prompt, how to verify, how to deploy — one at a time). Neither matches the actual shape of long-horizon AI-assisted work, which is a sequence of distinct activities with incompatible success criteria.

This paper reports an architecture that emerged empirically from a real project — a local, hybrid RAG tool for grounding technical claims against indexed papers (`local-quantum-rag`) — and was then compared, after the fact and not as a starting foundation, against existing literature on divergent/convergent thinking, iterative self-refinement, and cost-aware model cascades. The correspondence is reported as *framing*, not as derivation.

The architecture has four layers. **Exploration** turns an intuition into a working prototype, using a cheap high-context model for many iterations, with execution happening outside the model's session. **Verification** changes the success criterion entirely: the question is no longer "does it work?" but "does it implement what the literature states?", and it is carried out by a stronger model with retrieval access to the source papers, under a set of standing constraints on the agent's behavior. **Discovery** moves the result into a public, reproducible environment. **Production** integrates it into a real software library under engineering controls.

Two claims distinguish this architecture from a generic four-step process description.

First, **the documentation of the architecture is asymmetric, and this asymmetry is a property of the architecture, not a gap.** Layer 1 does not have a dedicated process document because it does not need one; Layers 2–4 do, because the criterion of success changes from "explored" to "verified" to "reproducible" to "shippable", and each transition requires explicit controls that a conversational phase does not require.

Second, **model choice is part of the method.** Each layer assumes capabilities that differ across models — a very large context window with near-zero per-iteration cost in Layer 1; strong reasoning plus retrieval grounding in Layer 2; paid-tier agentic coding in Layer 4 — and substituting a different model changes what the layer can do, not merely how fast it does it. Models differ in structural properties (how many sub-agents they spawn, how they handle tool integration, how they manage their own context), and these differences are not incidental to the method.

Within Layer 2 we report a concrete failure mode. A standing instruction to reload the agent's operating rules was scoped only to conversation compaction events, leaving a real gap at plain session start. The two events are the same failure condition (loss of, or absence of, a fully-loaded rule context) reached by two different paths; the fix was to widen the trigger to name both. We treat this as evidence for a general principle: a static instruction only constrains behavior at the specific trigger points it names, and coverage gaps are found by tracing *every* path that produces the failure state, not only the path that was top of mind when the instruction was written.

The remainder of the paper is structured as follows. Section 2 gives an overview of the four layers and their properties. Section 3 covers Layer 1. Section 4 covers Layer 2 in depth, including the `local-quantum-rag` grounding tool, the agent's operating constraints, and the reload-gap case study. Section 5 covers Layer 3. Section 6 covers Layer 4. Section 7 discusses the documentation asymmetry and the process/constraint distinction. Section 8 situates the architecture against related work. Section 9 states limitations. Section 10 concludes.

---

## 2. The Four-Layer Architecture

### 2.1 General schema

The architecture can be represented as a sequence of four phases, each with its own environment, type of knowledge, success criterion, and set of controls. The fundamental principle is that the four phases **are not interchangeable**: each solves a different problem.

```
                 ┌──────────────────────────┐
                 │  HUMAN INTUITION         │
                 │  Interest / analogy      │
                 │  hypothesis / question   │
                 └────────────┬─────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│ LAYER 1 — EXPLORATION AND IMPLEMENTATION                 │
│ DeepSeek + Google AI for search                          │
│ Idea → literature → context → code → experiment          │
│ → debugging → prototype                                  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ LAYER 2 — SCIENTIFIC VERIFICATION                        │
│ Opus 5 + local-quantum-rag                               │
│ Code → paper → mathematics → verification → cross-check  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ LAYER 3 — DISCOVERY                                      │
│ Public environment / GitHub                              │
│ Documentation → experiments → tests → reproducibility    │
│ → coverage → shared memory → validation                  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ LAYER 4 — SOFTWARE / PRODUCTION                          │
│ Real library                                             │
│ Integration → API → tests → CI → compatibility           │
│ → guardrails → release                                   │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
                    NEW RESULTS
                           │
                           ▼
                    NEW INTUITION
```

### 2.2 Layer table

| Layer | Environment | Main question | Output |
|---|---|---|---|
| **1. Exploration** | DeepSeek | Can we turn the idea into an experiment? | Prototype |
| **2. Verification** | Opus 5 + local-quantum-rag | Does the prototype correctly implement the science? | Verified implementation |
| **3. Discovery** | GitHub / public environment | Can we document and reproduce the result? | Public, reproducible result |
| **4. Production** | Library / CI | Can we integrate it without breaking the software? | Release |

### 2.3 The four levels of control

The architecture can also be read as a progression of four kinds of control, which are not equivalent:

- **Level 1 — Experimental control**: *Does it work?*
- **Level 2 — Scientific control**: *Is it correct with respect to theory and the literature?*
- **Level 3 — Epistemic control**: *Is it documented, reproducible, and checkable by others?*
- **Level 4 — Engineering control**: *Is it stable, integrable, and maintainable in real software?*

A program can work but be scientifically wrong. It can be scientifically correct but poorly documented. It can be scientifically correct and well documented but break the library. The architecture exists precisely to **avoid conflating these four problems**.

### 2.4 Asymmetric documentation

A structural property of the architecture, which the rest of the paper documents: the four layers are not documented in the same way. Layer 1 has no dedicated process document. Layers 2–4 do, and Layer 2 is the documentation's center of gravity: it is the only layer that has, simultaneously, a detailed process document (`draft_verification_methodology.md`), a constraint document (`operational_constraints.md`), a failure-mode case study (`context_engineering_case_study.md`), and a tool that makes it reproducible (`local-quantum-rag`).

This asymmetry is not a shortcoming. Layer 1 is a divergent, conversational phase in which an error is not a methodological failure and a hypothesis can be discarded without anything needing to be documented beyond the final result. From Layer 2 onward the success criterion changes, and with it the documentation obligation.

---

## 3. Layer 1 — Exploration and Implementation

### 3.1 Goal

Layer 1 exists to turn an **intuitive direction** into a concrete computational object. There is no claim yet to definitively prove the idea's scientific correctness. The main question is:

> **"Can we turn this intuition into a working experiment?"**

### 3.2 The human trigger

The process starts from the operator's own interest. The trigger can be a documentary, an image, a theory, a formula, something read, an observed problem, a personal experience, a random association, a passion, an apparently naive question. The Minkowski diagram example is representative: observing a geometric structure can generate the idea of relating it to an already-studied quantum problem. It is not yet a theory. It is a **direction to explore**.

### 3.3 Attention and curiosity

The intuition requires attention. The operator must be sufficiently engaged with the problem to recognize relationships that were not explicitly being searched for. In this phase: **interest → attention → association → hypothesis.** An error is not a methodological failure; a hypothesis can be discarded.

### 3.4 First experiment

The first idea is quickly turned into a sketch or a small implementation. If the result produces nothing, the hypothesis is modified or abandoned. The principle is:

> **first check experimentally whether something exists at all, then invest further in the direction that shows potential.**

### 3.5 Brainstorming with the AI

The conversational AI is used as a processing space. The goal is not necessarily to obtain the solution immediately: the conversation serves to make the idea explicit, formulate questions, identify possible connections, generate hypotheses, identify problems, and turn vague intuitions into technical questions. The AI thus becomes an **amplifier of the exploratory process**.

### 3.6 State-of-the-art search

Before seriously implementing a new idea, a literature search is carried out: original papers, recent work, related algorithms, existing implementations, results already obtained, known limitations. The purpose is to avoid presenting as new an idea that has already been studied.

### 3.7 Gathering papers

The relevant scientific documents are downloaded and organized. The user does not necessarily need to study all of them in depth immediately: the initial phase mainly consists of building a **document map of the problem**. The papers become operational material for the AIs.

### 3.8 Building the context

The Layer 1 model receives a context made up of existing code, architecture, the project's style, papers, documentation, previous results, the idea to implement, and the experimental goal. The problem is thus transformed from:

> "Write an algorithm."

into:

> **"Integrate this new scientific idea into this specific software system."**

### 3.9 The limit of the AI as information

When the model runs into a difficulty, the response is not to force it to keep going. The question asked is:

> **"What is missing for you to be able to answer?"**

The model can identify mathematical knowledge, papers, formulas, techniques, references, contextual information. These gaps become new research tasks.

### 3.10 Orchestration across multiple AIs

Difficult questions can be handed off to another system. One model's limit becomes the next one's input:

```
DeepSeek → unresolved question → Google AI / another AI → partial answer
→ new questions → additional papers → DeepSeek
```

### 3.11 Implementation

Once the context is sufficient, the model generates the code. The implementation can include new functions, modules, algorithms, applications, tools, integrations with the existing library. These are not necessarily small changes: a single idea can produce a significant amount of new code.

### 3.12 Experimental execution

The code is run, for example, in Google Colab. The experimental environment makes it possible to keep separate **exploratory code** from **production software**. The results are then concretely observed.

### 3.13 Iterative debugging

When an error appears:

```
Code → Execution → Error → Output / traceback
→ Model → Fix → New execution
```

The cycle can repeat many times. Debugging becomes an integral part of the methodology.

### 3.14 Output of Layer 1

The phase ends when there is a **working experimental prototype, documented enough to be submitted to scientific verification.**

### 3.15 Why Layer 1 has no dedicated process document

Layer 1 is documentable — it has twelve distinct steps — but it does not need a dedicated process document because it is already the simplest thing in the architecture: loading documents into a chat, brainstorming, obtaining code, testing it, debugging. The documentation weight lies from Layer 2 onward, because that is where the work becomes convergent and verifiable, and where the success criterion changes. Documenting Layer 1 beyond this level would be documentation for its own sake.

---

## 4. Layer 2 — Scientific Verification

### 4.1 Change of success criterion

Layer 2 completely changes the success criterion. The question is no longer:

> "Does the code work?"

but:

> **"Does the code actually implement what the scientific literature states?"**

### 4.2 The model and the tool

Layer 2 uses a strong reasoning model (in this project's practice, Opus 5) together with `local-quantum-rag`, a local, hybrid RAG tool that indexes the original papers on disk and returns, for a given verification question, the passages that actually contain the answer. The schema is:

```
Code → verification question → local-quantum-rag
→ original paper → relevant passage → model → verification
```

`local-quantum-rag` is described in detail in Section 4.3. The point here is that Layer 2 does not trust the model's memory: every technical conclusion passes through the tool before being written.

### 4.3 The tool: local-quantum-rag

`local-quantum-rag` is a small, local, hybrid RAG tool: it indexes PDFs and Markdown notes on disk, then answers a question by returning the passages that actually contain the answer — no server, no vector database, no cloud calls beyond the one-time download of the (open) embedding and reranker models.

The operational flow has four steps.

**Step 1 — Index a folder of documents.** Every document lives under `papers/<collection>/`. A collection is its own independent vocabulary space, so unrelated topics never dilute each other's retrieval. The command:

```bash
python build_index.py --collection quickstart
```

reads every `.pdf`/`.md`/`.txt` file, splits it into chunks, fits a TF-IDF vectorizer over the chunks, and computes a dense embedding per chunk (`sentence-transformers/all-MiniLM-L6-v2`). Everything is written to `index/<collection>/` — vectorizer, TF-IDF matrix, chunk text, embedding matrix — so this step only needs to run again when the source documents change.

**Step 2 — Ask a question in plain language.**

```bash
python query.py --collection quickstart "why does semantic search sometimes miss a specific fact"
```

The query is scored two ways at once, then combined: TF-IDF cosine similarity (rewards exact word overlap) and dense-embedding similarity (catches paraphrases and synonyms the TF-IDF pass misses — Karpukhin et al. 2020). The union of both candidate pools is reranked by a cross-encoder, which reads the query and each passage together rather than comparing precomputed vectors; that final ranking is what gets printed.

**Step 3 — Pin down an exact fact the ranking buries.** Step 2's top result talks *about* exact-match search, but the specific fact it exists to demonstrate — "the answer is 42 kelvin" — is a short, non-central sentence a purely topical ranking has no reason to place first. `--exact` skips retrieval entirely and searches the raw chunk text directly:

```bash
python query.py --collection quickstart --exact "the answer is 42 kelvin"
```

Literal mode is case-insensitive substring matching. `--regex` treats the pattern as a real, case-sensitive regular expression — useful for a fixed value with a known shape (`\d+\.\d+ mg/kg`) rather than an exact phrase.

**Step 4 — Skip the reranker when speed matters more than precision.** The cross-encoder in Step 2 is the slowest part of the pipeline, since it re-reads every candidate passage. `--no-rerank` returns the raw TF-IDF ranking. In this mode neither the embedding model nor the cross-encoder is loaded at all — only the TF-IDF vectorizer from Step 1 — so it starts faster and needs no model download on a machine that has never run this tool before.

**Why "atomic," not just "quantum."** The name comes from the author's original domain, quantum computing, not a metaphor — but the design is atomic in three literal senses: collections are isolated vocabulary spaces that never merge; each query is served the smallest chunk that answers it, not a whole document; and the tool exists specifically to support a verification method (Section 4.4) that proceeds one step at a time, never beyond what was asked.

### 4.4 The verification method: two sub-phases, Draft and Review

Within Layer 2, the work is organized into two sub-phases with opposite goals. These are not the same activity done with more or less care: they have opposite goals, tools, and success criteria, and mixing them produces a worse result than either taken alone.

**Divergent sub-phase — the Draft.** Goal: explore. Understand a paper's logic, translate it into code, see whether the idea holds up — without yet having to defend it all the way through. Tool: a free AI with a very large context window (on the order of a million tokens) — in current practice, DeepSeek's free tier. The choice is not incidental: this phase can require many repetitions, so it runs on a tool whose per-iteration cost is close to zero.

Procedure: load the original papers into the AI; build an understanding of the paper's logic together with the AI; have the AI emit the corresponding code; copy that code by hand and run it in an external test environment (Kaggle or Colab) — execution happens outside the session that generated the code; when a bug shows up, the fix goes back to the same "primary" AI for this phase, not treated as a side note: this way the AI has already dealt with that error by the next attempt and doesn't repeat it. Debugging is followed and pasted in by hand, never delegated blindly.

Exit criterion: the draft counts as complete **only** once it stops behaving like a draft — every test passes, every calculation has actually run and reached a concrete result. At that point it is treated as a finished project, not a sketch to be polished later.

Note: it happens that the draft's quality exceeds that of the subsequent review phase — that's a sign the brainstorming worked well, not an anomaly to correct.

Required mindset: during this phase, the human must also forget that a review phase will follow. Knowing in advance that another AI will "check everything afterward" lowers one's guard and produces a less rigorous draft — exactly the opposite of what's needed, since the review phase assumes the draft is already the best possible version, not a sketch to be corrected. The draft must be carried out as if it were the only, final chance: work any other way, and the draft simply doesn't work.

**Convergent sub-phase — the Review.** Goal: apply, not explore. No more brainstorming. Tool: a strong local AI, with real access to the source papers via RAG (`local-quantum-rag`), handed the already-complete draft — the best version Layer 1 could produce — together with the working code.

Task: debug and enforce every constraint from the constraints framework, within its own token budget, and check whether the draft actually honored every point described in the source text — not redesign it. This phase *is* the real project: it's where every operating rule actually gets applied.

When the numbers don't add up: dig into why and where, and log the failure so it isn't repeated — the same principle as Layer 1, applied at Layer 2's standard of rigor.

Tool for code: only a strong, paid-tier AI (Claude Code or an equivalent level). The one non-negotiable rule of this phase: the AI never proceeds on its own initiative — one point at a time, in order, never beyond what's asked.

### 4.5 The agent's operating constraints

Layer 2 is not just a verification method: it is also an agent operating under a set of constraints. These constraints do not belong to the other layers; they are specific to Layer 2, and their failure mode is the subject of the case study in Section 4.7.

**Context bootstrap (fixed trigger rule).** In the Context Engineering literature, *context management* — what persists, what is dropped, what is reloaded — is recognized as one of the field's foundational components alongside retrieval, generation, and processing (Mei et al., 2025). An agent does not automatically retain a set of behavioral constraints for a session's full duration: a rule file existing on disk is not the same as its content having actually been loaded into the model's active context.

**Trigger rule**: at the start of every new session, **and** after every conversation compaction (`/compact` — the operator that summarizes a long exchange to free context window space), the agent must explicitly reload its operating rule module (`session-rules`) before taking any other action.

The two trigger events are not distinct cases — they are the same failure condition (loss of, or absence of, a fully-loaded rule context) reached by two different paths. A compaction preserves a reference to a rule's existence, not its literal content; a fresh session simply never passes through the event that would trigger reloading, if that event is not also defined explicitly for session start.

**Project-specific constraint**: every technical conclusion must pass through the local retrieval-augmented generation system (this repository) before being written — no unverifiable assertion against the indexed sources. The process is traced explicitly: which queries were run, what they returned, why a given implementation choice followed from it.

**Budget constraint**: each session operates under a finite token budget (on the order of one million) and no implicit memory of a previous session's failed attempts on the same project. This implies a direct operating principle: every action should be targeted, not exploratory — abstract reasoning is resolved at the planning stage, leaving execution a narrow, mechanical path. A wasted operation is not merely an isolated cost: it is budget taken from a later, better-aimed attempt. Wu et al. (2026) formalize the same principle for long-horizon search agents as a sequential decision problem constrained by an explicit context budget (the BACM framework), reporting gains of over 1.6x versus unconstrained baselines precisely from choosing selectively *when* to compress, rather than compressing uniformly.

### 4.6 The codified operating rules (`session-rules`)

Full content of the module reloaded at bootstrap, not a summary of it.

**Token-budget discipline**

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

**Technical documentation conventions (project-specific, Dense-Evolution).** Sixteen numbered rules requiring: a progressive-guide structure (not a pure API reference); conceptual ground-zero before showing code; incrementally-built numbered steps; self-contained code blocks; no inline comments (explanations live in prose); short variable naming; a single canonical solution per step, with alternatives confined to a closing section; real functions invoked directly, never behind opaque wrappers; bug provenance and history isolated to a closing "Details" section; no self-referential narration by the agent within the guide; every reported numeric value must have been executed and verified, never estimated.

### 4.7 Case study: the reload gap

**The system under study.** The Layer 2 agent operates under a layered constraint system:

1. A fixed, always-in-force instruction, stored outside the conversation (`CLAUDE.md`), naming *when* to reload the operating rule set.
2. A skill file (`session-rules`) containing the actual rule content: token-economy discipline (the nine numbered rules above) and a project-specific documentation style guide (sixteen numbered rules).
3. A cross-session memory store (~35 entries at time of writing), consulted contextually rather than reloaded in full each turn.
4. Tool-specific conventions that activate only while a given tool (version control, a publishing surface, a documentation-lookup service) is actually in use during a turn.

Layers 2 and 4 are not part of the model's persistent weights or default context — each is either invoked explicitly (layer 2) or supplied by the tool integration itself at call time (layer 4).

**The incident.** The fixed instruction (layer 1) read: reload the rule set "after every `/compact`". This correctly anticipated one real failure mode: a summarization pass drops the literal rule text while preserving only a reference to its existence, so the rule content must be explicitly reloaded afterward.

It did not anticipate a second, functionally identical failure mode: a session that begins fresh (no prior compaction in its own history) never triggers the instruction at all, since no `/compact` event has yet occurred. The rule file exists on disk in both cases; in neither case does its existence alone place its content into the model's active context. The two triggers are not distinct problems requiring separate handling — they are the same event (loss of, or absence of, a fully-loaded rule context) reached by two different paths.

**Fix and verification.** The fixed instruction was revised to name both trigger conditions explicitly: session start, in addition to post-compaction. Verification consisted of invoking the rule-reload skill immediately after the edit, confirming it executes at the point of failure previously left uncovered, and cross-checking the skill file itself for completeness against the rule content it was meant to reproduce verbatim (found to already be complete and current at the time of this fix).

**What it shows.** This incident is a small, concrete instance of the general principle in the budget-aware and self-governing context literature: a static instruction, however correctly written, only constrains behavior at the specific trigger points it names. Coverage gaps are found by tracing *every* path that produces the failure state the instruction was meant to prevent (here: an under-loaded rule context), not only the path that was top of mind when the instruction was first written. The fix required no new mechanism — only widening an existing trigger condition to match the actual failure surface.

**Why it is internal to Layer 2.** The reload gap is not a Layer 1, 3, or 4 problem. It is specific to Layer 2 because that is where there is an agent operating under standing constraints across multiple sessions. Layer 1 has no such constraints; Layers 3 and 4 have engineering controls (guardrails, CI) that do not depend on the agent's memory. Layer 2 is the only layer where the constraint is *behavioral*, and therefore the only one where a behavioral constraint can fail silently.

### 4.8 Cross-session persistent memory

An accumulated observation store (~35 entries at time of writing), consulted for contextual relevance rather than reloaded in full every turn — a two-tier memory architecture (working context vs. long-term store) consistent with what is described for long-horizon agent systems in the Context Engineering literature. Representative entries:

- Token-economy discipline, as a cross-cutting operating principle.
- Verification of a published artifact via actual browser loading, never from source code alone.
- Prohibition on delegating literature research to sub-agents when direct action is available.
- Prohibition on isolation in parallel working environments (worktrees) absent an explicit request.
- Mandatory serialization of heavy computational loads, never run in parallel without warning.
- Rules of engagement for security testing: demonstrate a vulnerability, never exploit it.
- Scope verification before any structural promotion of a module (code, tests, CI, documentation), to avoid duplicating existing work.

### 4.9 Baseline behavioral constraints

Independent of the specific project:

- No feature or abstraction beyond what the task requires.
- No error handling for cases that cannot occur.
- Code comments only for non-obvious rationale, never descriptive of the obvious.
- Explicit confirmation required before an irreversible or high-impact action (force-push, deletion, external publication), absent specific prior authorization.
- Version-control state verification before commands that could discard unsaved work.
- No bypassing a safety check instead of resolving its underlying cause.

### 4.10 Tool-specific constraints (conditional activation)

Not a fixed, known-in-advance list: each integration (version control, a publishing surface, a documentation-lookup service) introduces its own operating conventions, active only for the duration of the turn in which that tool is actually invoked — a direct instance of the "just-in-time context" principle described in Mei et al. (2025) for external tool integration in an agentic architecture.

### 4.11 Closing methodological note on Layer 2

None of these levels is kept active by repeated re-reading every turn. Levels 1, 2, and 4 persist in context once loaded; level 3 is queried for relevance; level 5 activates only on actual use of the corresponding tool. Over a long or thematically heterogeneous session, one level can be applied correctly while another is missed — precisely the condition the bootstrap rule (Section 4.5) was revised to cover fully.

---

## 5. Layer 3 — Discovery

### 5.1 Goal

This layer must be kept conceptually separate from the first two. **Discovery is not brainstorming.** It is the environment in which new experimental knowledge is made public, checkable, and shareable. Its purpose is to run an idea against reality before it is allowed to affect anything real: not a staging area for code that is already believed correct, but a place where being wrong is the expected, normal outcome of most entries, and is recorded exactly as carefully as being right.

### 5.2 Moving into the Discovery space

The project is brought into the public environment, typically GitHub. Here the rule system changes. The code is no longer "something that works on my computer": it becomes **"something that must be able to be examined by others."**

### 5.3 Rules specific to this environment

The Discovery layer contains dedicated instructions covering documentation, experiments, tests, claims, coverage, reproducibility, project structure, and verification methodology. The rules are not simply contained in the AI's prompt: they are embedded in the environment.

### 5.4 Structural rules

1. **One script per idea, runnable standalone.** Every entry is a single script that produces its own result end to end — never a module other entries import from. This keeps ideas independent: a later finding can contradict an earlier one without any code needing to change.
2. **A test mirrors a script only when the script's own claim needs re-checking automatically.** Not every entry needs one — an exploratory script that already recorded its one-time result in its write-up does not need to be re-run forever; a script whose claim later gets relied on elsewhere does.
3. **No publishing gate.** Version freely, one bump per entry recorded, independent of any package index. The cost of being wrong here is a documented negative result, not a broken release.
4. **A negative result is written up with the same care as a positive one**, and is not deleted or hidden once found to be wrong — it is marked as resolved and left in place, so the next attempt (human or AI) does not repeat it. The single most common way a promising-looking result turns out to be wrong: check it against a **negative control** — rerun the exact same analysis on data known to contain no real effect (shuffled order, a randomized label, a mismatched baseline) — and see whether the "effect" survives. If it appears identically in both, it was never a real effect.
5. **Promotion out of Discovery is deliberate and one-directional.** A result moves into the Evolving Software repository only after being independently re-verified — never automatically, never because it merely exists here.

### 5.5 Documentation

Every result must be reconstructible. The documentation links:

```
Idea → Paper → Method → Code → Experiment → Result
```

This creates a persistent memory.

### 5.6 Shared human–AI memory

The documentation has a second function. It becomes a memory that can be consulted by the author, collaborators, other AIs, reviewers, future developers. A different AI can be tasked with reading a GitHub page and looking for errors. The repository thus becomes a **shared-memory substrate**.

### 5.7 Transparency of the AI's own work

The documentation makes it possible to check whether the system actually understood its own work. The AI must be able to explain what it implemented, why, from which paper, which formula it uses, how it was verified, what the limitations are.

### 5.8 Reproducible experiments

Experiments must be repeatable. What must be defined: conditions, inputs, parameters, environment, expected outputs, metrics, success criteria. The discovery is thus turned from a personal experience into a **reproducible object**.

### 5.9 Scientifically meaningful tests

Tests must not be limited to trivial cases. They must also check edge cases, properties, known results, expected behavior, numerical stability, comparison against references.

### 5.10 Cross-validation

The result must match, when possible, an independent reference:

```
New implementation → result
        ↕
reference implementation → result
```

Agreement constitutes a further level of verification.

### 5.11 Discovery guardrails

The environment can automatically block progression when a condition is not met:

```
test failed → pipeline blocked
insufficient coverage → change not accepted
```

This matters because the system must not depend solely on the AI's ability to remember every rule.

### 5.12 Output of Layer 3

The phase produces **a public, documented, reproducible result, tested and subjected to independent checks.**

---

## 6. Layer 4 — Production

### 6.1 Goal

The last layer is completely different from Discovery. The question is no longer:

> "Is the experiment interesting?"

The question is:

> **"Can this new component stably enter a real software library?"**

The real repository is the one users install. Only what a Discovery repository's negative controls did not kill reaches this point — and the standard of care here is higher, not equal, because a mistake here reaches people who were never part of the process that produced it.

### 6.2 Adapting the code

The experimental code is not necessarily carried over directly. What may be needed: refactoring it, changing its API, adapting it to the architecture, removing experimental code, improving error handling, integrating dependencies, adding documentation.

### 6.3 Integration into the library

The new component must coexist with pre-existing code, APIs, dependencies, versions, operating systems, other features. The problem thus becomes systemic.

### 6.4 Structural rules

1. **The list of what actually ships must be kept honest.** Any packaging configuration that names distributable components by hand (rather than discovering them automatically) is a list that *will* drift the moment a new component is added and the list is not updated in the same commit — a real, recurring failure mode, not a hypothetical one: a component can pass every local test (tests run against the source tree directly) while being silently absent from what actually gets built and shipped, and the gap is only found once an independent installer hits a real import error. Check the shipped list against the real directory tree as part of building every release, not only when something breaks.
2. **A release is never manually declared correct — the platform enforces it structurally.** Configure the hosting platform so that merging to the branch users build against is physically refused until a named set of checks reports success. This is not a courtesy; it is the difference between "nobody remembered to check" and "it is not possible to skip checking."
3. **Publishing to a package index is a distinct, separate, human-confirmed step from everything before it — never automated away.** Build the distributable artifact, verify its metadata independently of the build step that produced it, and only *after* a human confirms the upload actually succeeded does the repository's own permanent record (a version tag, a public release note) get created. A tag or release created before that confirmation can end up pointing at something that was never actually published, or at a version number that had to be abandoned after publishing failed partway.
4. **Versioning communicates what changed, honestly.** New capability that does not break anything existing is a different kind of change from a same-behavior fix — pick the version-number position that matches which one actually happened, not whichever feels more exciting.
5. **A red status check is not a single category.** Before reacting, determine which of three things actually happened: a real defect in the change (fix at the root, not by rerunning); already-documented infrastructure noise unrelated to the change (confirmed by reading the actual failure, not assumed — then safe to simply retry); or a defect the test suite itself cannot see at all (rule 1 above is the standing example — caught only by a real, independent consumer actually installing the real artifact, never by the suite that built it).

### 6.5 Regression tests

A new feature must not break what already worked:

```
new feature + existing code → no regression
```

### 6.6 CI and automation

The automated pipeline runs the checks without requiring a full manual review on every change. This shifts the checking from the operator's memory to the machine.

### 6.7 Codecov and coverage

Coverage checks how much of the new and modified code is actually exercised by the tests. It is not, by itself, proof of scientific correctness, but it is one of the engineering mechanisms that contribute to the product's robustness.

### 6.8 Cross-platform compatibility

The library is checked across multiple configurations. In the case described here: 3 macOS environments, 3 Ubuntu environments, around 1,344 tests per environment (verified against a real CI run). Total: **over 8,000 test executions.** This reduces the risk that a change only works in the author's own environment.

### 6.9 Production guardrails

The principle is:

> **if a critical condition is not met, the release does not proceed.**

For example:

```
Tests failed → PUSH BLOCKED
Insufficient coverage → PUSH BLOCKED
```

Guardrails thus turn rules from recommendations into **operational constraints**.

### 6.10 Release

Only after the pipeline is passed can the new component be included in the production software. At this point the path is:

```
Intuition → Experiment → Scientific verification
→ Public Discovery → Integration → CI / Tests / Coverage → Release
```

### 6.11 Failure mode this layer exists to prevent

Confusing "every test passed" with "this is safe to give to someone else" — a coverage number, a green checkmark, and a successful build are each evidence toward that conclusion, not proof of it individually or together.

---

## 7. Discussion

### 7.1 The documentation asymmetry is a property, not a gap

The four layers are not documented in the same way, and this is deliberate. Layer 1 has no dedicated process document because its activity is already the simplest in the architecture: loading documents into a chat, brainstorming, obtaining code, testing it, debugging. Layers 2–4 have dedicated process documents because the success criterion changes at every transition, and every transition requires explicit controls that a conversational phase does not require.

This asymmetry is not a completeness defect. It is the recognition that documentation has a cost, and that the cost is justified only where the success criterion is convergent and verifiable.

### 7.2 Models are part of the method

Each layer assumes specific capabilities:

- **Layer 1**: a very large context window (on the order of a million tokens), near-zero per-iteration cost, willingness to run many iterations.
- **Layer 2**: strong reasoning, retrieval access via RAG, ability to operate under standing behavioral constraints across multiple sessions.
- **Layer 3**: ability to operate in a public environment with rules embedded in the environment itself.
- **Layer 4**: paid-tier agentic coding, with the ability to integrate into a real library under engineering controls.

Substituting one model for another is not a change of vendor: it is a change of what the layer can do. Models differ in structural properties — how many sub-agents they spawn, how they handle tool integration, how they manage their own context — and these differences are not incidental to the method. This is why model names are kept explicit in the paper: not as an endorsement, but as part of the description of what the method assumes.

### 7.3 The process/constraint distinction

A distinction the paper has inherited from its source documents and which we did not find explicitly formulated in the literature we surveyed: **documents divide into two classes, with different addressees.**

- **Process documents**: they describe how a human researcher organizes their own work over time, using multiple AI assistants in different roles. They are not addressed to an AI and should not be handed to an AI as an operating instruction. An assistant reading them as rules would try to execute "first phase 1, then phase 2" on itself — which makes no sense, because the two phases are carried out by two *different* AIs, deliberately chosen for opposite roles.
- **Constraint documents**: they are addressed to an AI. They specify what the agent must do, when, and under what conditions.

The distinction explains why the reload gap exists. Constraint documents must be reloaded at defined triggers, because their reader is the agent. Process documents are not, because their reader is the human. Confusing the two classes — treating a process document as a constraint, or vice versa — produces symmetric failure modes: an agent trying to execute a process that is not its own, or a human expecting a constraint to apply without having been activated.

### 7.4 The reload gap as a general instance

The reload gap is not an isolated bug. It is an instance of a general principle that runs through the whole architecture: **a static instruction only constrains behavior at the specific trigger points it names.** Coverage gaps are found by tracing *every* path that produces the failure state the instruction was meant to prevent, not only the path that was top of mind when the instruction was first written.

This principle has an operational corollary: when writing a behavioral constraint for an agent, the right question is not "does this constraint cover the case I have in mind?" but "what are *all* the paths that produce the state this constraint must prevent?" The reload gap is what happens when the first question is answered instead of the second.

---

## 8. Related Work

The method described in this paper arose empirically — it was not derived from the works below. The correspondence was verified after the fact, not used as a starting foundation; it should be read as *framing*, not as a pre-existing theoretical basis.

**The four-layer structure as a whole** matches the distinction between *divergent* and *convergent* thinking introduced by Guilford in his structure-of-intellect model (Guilford, 1956), and operationalized as a two-phase process by the UK Design Council's "Double Diamond" model (Design Council UK, 2005): a phase that generates and explores possibilities (*discover*), followed by a phase that evaluates, selects, and refines (*define*) — precisely the relationship between Exploration and Verification described here. The separation between Discovery and Production, however, corresponds to a distinction the Double Diamond does not make: the passage from "public, reproducible result" to "stable component in a real library" is a change of success criterion that the design-process literature does not capture, because it assumes the outcome of the process is already a product.

**Layer 1's internal mechanism** (emit code, test it, feed the error back to the same AI so it isn't repeated) converges with two recent threads in LLM-agent research: Self-Refine (Madaan et al., 2023), where the same LLM generates an output, critiques it, and refines it iteratively with no extra training required; and Reflexion (Shinn et al., 2023), where the agent doesn't update its own weights but keeps a textual memory of past failures to avoid repeating them on later attempts — the exact principle behind "the debug is followed and pasted in by hand, so the AI has already dealt with it by the next attempt."

**The cost asymmetry between layers** (a free AI for many iterations in Layer 1, an expensive AI for one rigorous pass in Layer 2) converges with the model-cascade logic described in FrugalGPT (Chen, Zaharia & Zou, 2023): use a cheap model for the bulk of exploratory work and reserve the expensive model for the pass that actually matters, reaching the same result — or better — at a fraction of the cost.

**Layer 2's budget constraint** (every action targeted, not exploratory) converges with Wu et al.'s (2026) formalization as a sequential decision problem constrained by an explicit context budget (the BACM framework), reporting gains of over 1.6x versus unconstrained baselines in high-complexity, long-horizon settings. The operating principle is the same: choose selectively *when* to compress, rather than compressing uniformly.

**The reload gap** converges with the thread on self-governing context (Self-GC) and on agents that treat their own context state as an observable signal ("LLM Agents Are Latent Context Managers"): an agent must actively re-assert its operating rules at defined trigger points, rather than assuming they persist by default once written.

**The separation of layers** finally resonates with Mei et al.'s (2025) distinction among the foundational components of Context Engineering — retrieval, generation, processing, management — and in particular with the "just-in-time context" principle for external tool integration in an agentic architecture, which Layer 2 directly instantiates (Section 4.10).

---

## 9. Limitations

This paper is an *experience report*, not a controlled study, and should be read as such.

1. **N = 1.** The architecture emerged from a single project. There is no comparison with a control group, nor with an alternative architecture applied to the same project. Claims about the architecture's properties are claims about *this* instance, not about a class.

2. **The case study is a single instance.** The reload gap is a concrete failure mode, but it is a single case. The generalization to the principle "a static instruction only constrains at the triggers it names" is supported by convergence with the literature (Section 8), not by an experiment.

3. **No comparative measure.** There are no baselines, no efficiency or quality metrics that can be compared. The "1.6x" reported in Section 4.5 is from Wu et al. (2026), not ours. The CI numbers (Section 6.8) are a scale datum, not a measure of the method's effectiveness.

4. **The 2026 references are preprints**, not peer-reviewed at the time of writing, and are cited with that caveat. The convergences declared in Section 8 were verified after the fact and do not constitute a theoretical derivation.

5. **Model names are contingent.** DeepSeek, Opus 5, and Claude Code are the models used in this project's practice at the time of writing. The structural properties the paper assumes (context window, per-iteration cost, agentic behavior) may change between versions and between models, and the paper's claims should be read as relative to this configuration, not as universal properties.

6. **Layer 1 is described more synthetically than Layers 2–4**, and this reflects the documentation asymmetry discussed in Section 7.1. It is not a presentation choice: it is a property of the architecture, but it makes Layer 1 less externally verifiable than the subsequent layers.

7. **The process/constraint distinction (Section 7.3) has not been validated.** We did not find explicit formulations in the literature we surveyed, but this does not mean they do not exist in literature we did not consult. We present it as an observation, not as a result.

---

## 10. Conclusion

The strength of the architecture does not come from the isolated use of any one particular AI. It comes from the **separation of responsibilities.** Each layer has its own environment, function, type of knowledge, success criterion, and set of controls.

The general principle can therefore be formalized as:

> **Intuition → Exploration → Verification → Discovery → Industrialization → new observation → new intuition.**

Artificial intelligence thus becomes a **multiplier of the human research process**, not necessarily a substitute for the initial act of imagination. The human side generates the direction. The AIs amplify the ability to explore it. The papers supply the scientific reference. The RAG keeps the connection to the sources. Discovery builds the public memory. The tests supply independent checks. CI and the guardrails prevent known errors from passing undisturbed through the pipeline. Production, finally, turns the experimental result into a stable software component.

The result, then, is not simply a program generated by an AI. It is the product of a pipeline in which intuition, scientific knowledge, artificial intelligence, experimentation, verification, and software engineering are deliberately kept separate and then recomposed into a single research process.

Two observations close the paper. First, the asymmetric documentation of the architecture — light in Layer 1, dense in Layers 2–4 — is not a gap but a property: it reflects the fact that the success criterion changes at every transition, and that documenting has a cost justified only where the criterion is convergent and verifiable. Second, models are not interchangeable components: each layer assumes specific structural capabilities, and model choice is part of the method. The reload gap, finally, remains as an operational reminder: a static instruction only constrains behavior at the specific trigger points it names, and coverage is verified by tracing every path that produces the failure state, not only the one that was in mind when the instruction was written.

---

## References

1. J. P. Guilford, *The Structure of Intellect*, Psychological Bulletin, Technical Report 4 (1956).
2. Design Council (UK), *Eleven Lessons: A Study of the Design Process — The Double Diamond* (2005).
3. A. Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, arXiv:2303.17651 (2023).
4. N. Shinn, F. Cassano, E. Berman, A. Gopinath, K. Narasimhan, S. Yao, *Reflexion: Language Agents with Verbal Reinforcement Learning*, arXiv:2303.11366, NeurIPS 2023.
5. L. Chen, M. Zaharia, J. Zou, *FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance*, arXiv:2305.05176 (2023).
6. L. Mei, J. Yao, Y. Ge, Y. Wang, B. Bi, Y. Cai, J. Liu, M. Li, Z.-Z. Li, D. Zhang, C. Zhou, J. Mao, T. Xia, J. Guo, S. Liu, *A Survey of Context Engineering for Large Language Models*, arXiv:2507.13334 (2025).
7. Y. Wu, Y. Zheng, T. Xu, Z. Zhang, Y. Yu, J. Zhu, C. Ma, B. Lin, B. Dong, H. Zhu, R. Huang, G. Yu, *ContextBudget: Budget-Aware Context Management for Long-Horizon Search Agents*, arXiv:2604.01664 (2026). *(preprint)*
8. *Self-GC: Self-Governing Context for Long-Horizon LLM Agents*, arXiv:2607.00692 (2026). *(preprint)*
9. *LLM Agents Are Latent Context Managers: Eliciting Self-Managed Context via a Proprioceptive Dashboard*, arXiv:2606.30005 (2026). *(preprint)*
10. V. Karpukhin et al., *Dense Passage Retrieval for Open-Domain Question Answering*, arXiv:2004.04906 (2020).

If you want, I can also produce a LaTeX version (arXiv-ready, with proper section structure, bibliography, and figure environments), or a shorter conference-style version (~6 pages) if you're targeting a workshop rather than arXiv.
