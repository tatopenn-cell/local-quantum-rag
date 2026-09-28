# Methodological Architecture in Four Phases

## From Intuition to Scientific Discovery and Production Software

**Nature of this document**: this is an **overview** document, not a process document and not a constraint document. It describes the architecture as a whole — the four phases, why they are not interchangeable, and what each assumes. It does not replace [`draft_verification_methodology.md`](draft_verification_methodology.md) (the human-facing process) or [`operational_constraints.md`](operational_constraints.md) (the AI-facing rules), to which it defers for operational detail. It is written for a reader who wants to understand the shape of the whole before deciding which companion document to open next.

---

## Abstract

This document describes a four-phase architecture for AI-assisted research, developed empirically over the course of a real project and compared against existing literature only after the fact. The four phases — Exploration, Verification, Discovery, Production — are not interchangeable: each has its own environment, its own success criterion, its own model requirements, and its own controls. Two structural claims distinguish this architecture from a generic four-step process description. First, the documentation of the architecture is asymmetric, and this asymmetry is a property of the architecture, not a gap: Exploration is a divergent, conversational phase that does not require a dedicated process document; Verification, Discovery, and Production are convergent, verifiable, and therefore documented. Second, model choice is part of the method, not an interchangeable component: each phase assumes capabilities — context window size, retrieval grounding, agentic behavior, cost per iteration — that differ across models and determine what the phase can do. We close with the two distinctions this document inherits from its source materials and did not find explicitly formulated in the literature surveyed: the split between **process documents** (addressed to the human) and **constraint documents** (addressed to the AI), and the operational principle that a static instruction only constrains behavior at the specific trigger points it names.

---

## 1. Introduction

How does a human researcher structure work carried out jointly with several different AI systems, so that the result is reproducible, verifiable, and stable? The question is not new, but most existing answers are either *model-agnostic* (frameworks that assume any sufficiently capable LLM will do) or *single-phase* (how to prompt, how to verify, how to deploy — one at a time). Neither matches the actual shape of long-horizon AI-assisted work, which is a sequence of distinct activities with incompatible success criteria.

This document reports an architecture that emerged empirically from a real project — a local, hybrid RAG tool for grounding technical claims against indexed papers (`local-quantum-rag`) — and was then compared, after the fact and not as a starting foundation, against existing literature on divergent/convergent thinking, iterative self-refinement, cost-aware model cascades, and context-engineering. The correspondence is reported as *framing*, not as derivation.

The architecture has four phases. **Exploration** turns an intuition into a working prototype, using a cheap high-context model for many iterations, with execution happening outside the model's session. **Verification** changes the success criterion entirely: the question is no longer "does it work?" but "does it implement what the literature states?", and it is carried out by a stronger model with retrieval access to the source papers, under a set of standing constraints on the agent's behavior. **Discovery** moves the result into a public, reproducible environment. **Production** integrates it into a real software library under engineering controls.

The remainder is structured as follows. Section 2 gives the general schema and the four levels of control. Sections 3–6 cover the four phases in turn. Section 7 discusses the two structural claims — documentation asymmetry and models-as-method. Section 8 situates the architecture against related work. Section 9 states limitations. Section 10 concludes.

---

## 2. General schema

### 2.1 Architecture diagram

```
                 ┌──────────────────────────┐
                 │  HUMAN INTUITION         │
                 │  Interest / analogy      │
                 │  hypothesis / question   │
                 └────────────┬─────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 1 — EXPLORATION AND IMPLEMENTATION                 │
│ DeepSeek + Google AI for search                          │
│ Idea → literature → context → code → experiment          │
│ → debugging → prototype                                  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 2 — SCIENTIFIC VERIFICATION                        │
│ Opus 5 + local-quantum-rag                               │
│ Code → paper → mathematics → verification → cross-check  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 3 — DISCOVERY                                      │
│ Public environment / GitHub                              │
│ Documentation → experiments → tests → reproducibility    │
│ → coverage → shared memory → validation                  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 4 — SOFTWARE / PRODUCTION                          │
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

### 2.2 Phase table

| Phase | Environment | Main question | Output |
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

---

## 3. Phase 1 — Exploration and Implementation

### 3.1 Goal

Phase 1 exists to turn an **intuitive direction** into a concrete computational object. There is no claim yet to definitively prove the idea's scientific correctness. The main question is:

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

The Phase 1 model receives a context made up of existing code, architecture, the project's style, papers, documentation, previous results, the idea to implement, and the experimental goal. The problem is thus transformed from:

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

### 3.14 Output of Phase 1

The phase ends when there is a **working experimental prototype, documented enough to be submitted to scientific verification.**

### 3.15 Why Phase 1 has no dedicated process document

Phase 1 is documentable — it has twelve distinct steps — but it does not need a dedicated process document because it is already the simplest thing in the architecture: loading documents into a chat, brainstorming, obtaining code, testing it, debugging. The documentation weight lies from Phase 2 onward, because that is where the work becomes convergent and verifiable, and where the success criterion changes. Documenting Phase 1 beyond this level would be documentation for its own sake.

---

## 4. Phase 2 — Scientific Verification

### 4.1 Change of success criterion

Phase 2 completely changes the success criterion. The question is no longer:

> "Does the code work?"

but:

> **"Does the code actually implement what the scientific literature states?"**

### 4.2 The model and the tool

Phase 2 uses a strong reasoning model (in this project's practice, Opus 5) together with `local-quantum-rag`, a local, hybrid RAG tool that indexes the original papers on disk and returns, for a given verification question, the passages that actually contain the answer. The schema is:

```
Code → verification question → local-quantum-rag
→ original paper → relevant passage → model → verification
```

The point is that Phase 2 does not trust the model's memory: every technical conclusion passes through the tool before being written.

### 4.3 The verification method: two sub-phases

Within Phase 2, the work is organized into two sub-phases with opposite goals — a divergent **Draft** and a convergent **Review**. These are described in detail in [`draft_verification_methodology.md`](draft_verification_methodology.md) and are summarized here only to make the phase-level structure legible.

- **Draft (divergent).** Goal: explore. Tool: a free AI with a very large context window. Exit criterion: every test passes, every calculation has actually run and reached a concrete result. Required mindset: the draft must be carried out as if it were the only, final chance.
- **Review (convergent).** Goal: apply, not explore. Tool: a strong local AI, with real access to the source papers via RAG, handed the already-complete draft. One non-negotiable rule: the AI never proceeds on its own initiative — one point at a time, in order, never beyond what's asked.

### 4.4 The agent's operating constraints

Phase 2 is not just a verification method: it is also an agent operating under a set of constraints, described in full in [`operational_constraints.md`](operational_constraints.md). The constraints cover context bootstrap (reload at session start and after compaction), token-budget discipline, cross-session memory, and tool-specific conventions. They are specific to Phase 2 because Phase 2 is the only phase in which the constraint is *behavioral* — Phase 1 has no such constraints, and Phases 3–4 have engineering controls that do not depend on the agent's memory.

### 4.5 The reload gap

A concrete failure mode of the constraints system is documented in [`context_engineering_case_study.md`](context_engineering_case_study.md): a fixed instruction to reload the rule set was scoped only to conversation compaction events, leaving a real gap at plain session start. The two triggers are not distinct problems — they are the same failure condition (loss of, or absence of, a fully-loaded rule context) reached by two different paths. The fix required no new mechanism, only widening an existing trigger condition to match the actual failure surface. The general principle: **a static instruction only constrains behavior at the specific trigger points it names.**

### 4.6 Formal and mathematical verification

The model analyzes the relationship between formula, definition, algorithm, implementation, result. What gets analyzed: formulas, metrics, transformations, conditions, assumptions, parameters, edge cases. This is the phase in which conceptual knowledge is turned into formal verification.

### 4.7 Point-by-point check

The code is compared against the paper systematically:

```
Paper → definition → formula → algorithm → implementation → output
```

Each step must be consistent with the next.

### 4.8 Independent verification

The result is compared against reference implementations, known results, analytical formulas, independent applications, benchmarks. The goal is to prevent an internal error from being mistaken for a valid result.

### 4.9 Output of Phase 2

The result is a **scientifically verified implementation, explicitly connected to the reference literature.**

---

## 5. Phase 3 — Discovery

### 5.1 Goal

This phase must be kept conceptually separate from the first two. **Discovery is not brainstorming.** It is the environment in which new experimental knowledge is made public, checkable, and shareable. Its purpose is to run an idea against reality before it is allowed to affect anything real: not a staging area for code that is already believed correct, but a place where being wrong is the expected, normal outcome of most entries, and is recorded exactly as carefully as being right.

### 5.2 Moving into the Discovery space

The project is brought into the public environment, typically GitHub. Here the rule system changes. The code is no longer "something that works on my computer": it becomes **"something that must be able to be examined by others."**

### 5.3 Rules specific to this environment

The Discovery layer contains dedicated instructions covering documentation, experiments, tests, claims, coverage, reproducibility, project structure, and verification methodology. The rules are not simply contained in the AI's prompt: they are embedded in the environment.

### 5.4 Structural rules

Full detail in [`verification_layers.md`](verification_layers.md), Workflow 3. The essential structure:

1. **One script per idea, runnable standalone** — never a module other entries import from.
2. **A test mirrors a script only when the script's own claim needs re-checking automatically.**
3. **No publishing gate** — version freely, independent of any package index.
4. **A negative result is written up with the same care as a positive one**, and is checked against a **negative control** before being believed.
5. **Promotion out of Discovery is deliberate and one-directional.**

### 5.5 Documentation

Every result must be reconstructible. The documentation links:

```
Idea → Paper → Method → Code → Experiment → Result
```

### 5.6 Shared human–AI memory

The documentation becomes a memory that can be consulted by the author, collaborators, other AIs, reviewers, future developers. The repository thus becomes a **shared-memory substrate**.

### 5.7 Transparency of the AI's own work

The documentation makes it possible to check whether the system actually understood its own work. The AI must be able to explain what it implemented, why, from which paper, which formula it uses, how it was verified, what the limitations are.

### 5.8 Reproducible experiments

What must be defined: conditions, inputs, parameters, environment, expected outputs, metrics, success criteria. The discovery is thus turned from a personal experience into a **reproducible object**.

### 5.9 Scientifically meaningful tests

Tests must not be limited to trivial cases. They must also check edge cases, properties, known results, expected behavior, numerical stability, comparison against references.

### 5.10 Cross-validation

```
New implementation → result
        ↕
reference implementation → result
```

Agreement constitutes a further level of verification.

### 5.11 Discovery guardrails

```
test failed → pipeline blocked
insufficient coverage → change not accepted
```

This matters because the system must not depend solely on the AI's ability to remember every rule.

### 5.12 Output of Phase 3

The phase produces **a public, documented, reproducible result, tested and subjected to independent checks.**

---

## 6. Phase 4 — Production

### 6.1 Goal

The last phase is completely different from Discovery. The question is no longer:

> "Is the experiment interesting?"

The question is:

> **"Can this new component stably enter a real software library?"**

The real repository is the one users install. Only what a Discovery repository's negative controls did not kill reaches this point — and the standard of care here is higher, not equal, because a mistake here reaches people who were never part of the process that produced it.

### 6.2 Adapting the code

The experimental code is not necessarily carried over directly. What may be needed: refactoring it, changing its API, adapting it to the architecture, removing experimental code, improving error handling, integrating dependencies, adding documentation.

### 6.3 Integration into the library

The new component must coexist with pre-existing code, APIs, dependencies, versions, operating systems, other features. The problem thus becomes systemic.

### 6.4 Structural rules

Full detail in [`verification_layers.md`](verification_layers.md), Workflow 4. The essential structure:

1. **The list of what actually ships must be kept honest.**
2. **A release is never manually declared correct — the platform enforces it structurally.**
3. **Publishing to a package index is a distinct, human-confirmed step.**
4. **Versioning communicates what changed, honestly.**
5. **A red status check is not a single category** — distinguish a real defect from infrastructure noise from a defect the test suite cannot see.

### 6.5 Regression tests

```
new feature + existing code → no regression
```

### 6.6 CI and automation

The automated pipeline runs the checks without requiring a full manual review on every change. This shifts the checking from the operator's memory to the machine.

### 6.7 Codecov and coverage

Coverage checks how much of the new and modified code is actually exercised by the tests. It is not, by itself, proof of scientific correctness, but it is one of the engineering mechanisms that contribute to the product's robustness.

### 6.8 Cross-platform compatibility

The library is checked across multiple configurations. In the case described here: 3 macOS environments, 3 Ubuntu environments, around 1,344 tests per environment (verified against a real CI run). Total: **over 8,000 test executions.** This reduces the risk that a change only works in the author's own environment.

> *Note:* these numbers refer to a real CI run of the Dense-Evolution project. The pipeline is generalizable; the absolute values depend on the project.

### 6.9 Production guardrails

> **if a critical condition is not met, the release does not proceed.**

```
Tests failed → PUSH BLOCKED
Insufficient coverage → PUSH BLOCKED
```

Guardrails thus turn rules from recommendations into **operational constraints**.

### 6.10 Release

```
Intuition → Experiment → Scientific verification
→ Public Discovery → Integration → CI / Tests / Coverage → Release
```

### 6.11 Failure mode this phase exists to prevent

Confusing "every test passed" with "this is safe to give to someone else" — a coverage number, a green checkmark, and a successful build are each evidence toward that conclusion, not proof of it individually or together.

---

## 7. Discussion

### 7.1 The documentation asymmetry is a property, not a gap

The four phases are not documented in the same way, and this is deliberate. Phase 1 has no dedicated process document because its activity is already the simplest in the architecture. Phases 2–4 have dedicated process documents because the success criterion changes at every transition, and every transition requires explicit controls that a conversational phase does not require.

This asymmetry is not a completeness defect. It is the recognition that documentation has a cost, and that the cost is justified only where the success criterion is convergent and verifiable.

### 7.2 Models are part of the method

Each phase assumes specific capabilities:

- **Phase 1**: a very large context window (on the order of a million tokens), near-zero per-iteration cost, willingness to run many iterations.
- **Phase 2**: strong reasoning, retrieval access via RAG, ability to operate under standing behavioral constraints across multiple sessions.
- **Phase 3**: ability to operate in a public environment with rules embedded in the environment itself.
- **Phase 4**: paid-tier agentic coding, with the ability to integrate into a real library under engineering controls.

Substituting one model for another is not a change of vendor: it is a change of what the phase can do. Models differ in structural properties — how many sub-agents they spawn, how they handle tool integration, how they manage their own context — and these differences are not incidental to the method. This is why model names are kept explicit in this document: not as an endorsement, but as part of the description of what the method assumes.

### 7.3 The process/constraint distinction

A distinction this document inherits from its source materials and did not find explicitly formulated in the literature surveyed: **documents divide into two classes, with different addressees.**

- **Process documents**: they describe how a human researcher organizes their own work over time, using multiple AI assistants in different roles. They are not addressed to an AI and should not be handed to an AI as an operating instruction. An assistant reading them as rules would try to execute "first phase 1, then phase 2" on itself — which makes no sense, because the two phases are carried out by two *different* AIs, deliberately chosen for opposite roles.
- **Constraint documents**: they are addressed to an AI. They specify what the agent must do, when, and under what conditions.

The distinction explains why the reload gap exists. Constraint documents must be reloaded at defined triggers, because their reader is the agent. Process documents are not, because their reader is the human. Confusing the two classes — treating a process document as a constraint, or vice versa — produces symmetric failure modes: an agent trying to execute a process that is not its own, or a human expecting a constraint to apply without having been activated.

### 7.4 The full cycle

```
                    HUMAN
                      │
         intuition / attention
                      │
                      ▼
          ┌─────────────────────┐
          │ PHASE 1             │
          │ DEEPSEEK            │
          │ idea → code         │
          │ → experiment        │
          │ → debugging         │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ PHASE 2             │
          │ OPUS 5 + RAG        │
          │ code ↔ paper        │
          │ mathematics         │
          │ verification        │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ PHASE 3             │
          │ DISCOVERY           │
          │ documentation       │
          │ tests               │
          │ reproducibility     │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ PHASE 4             │
          │ SOFTWARE            │
          │ integration         │
          │ CI / coverage       │
          │ release             │
          └──────────┬──────────┘
                     │
                     ▼
              NEW RESULT → NEW OBSERVATION → NEW INTUITION
```

---

## 8. Related Work

The method described in this document arose empirically — it was not derived from the works below. The correspondence was verified after the fact, not used as a starting foundation; it should be read as *framing*, not as a pre-existing theoretical basis.

**The four-phase structure as a whole** matches the distinction between *divergent* and *convergent* thinking introduced by Guilford in his structure-of-intellect model (Guilford, 1956), and operationalized as a two-phase process by the UK Design Council's "Double Diamond" model (Design Council UK, 2005): a phase that generates and explores possibilities (*discover*), followed by a phase that evaluates, selects, and refines (*define*) — precisely the relationship between Phases 1 and 2 described here. The separation between Phase 3 and Phase 4, however, corresponds to a distinction the Double Diamond does not make: the passage from "public, reproducible result" to "stable component in a real library" is a change of success criterion that the design-process literature does not capture, because it assumes the outcome of the process is already a product.

**Phase 1's internal mechanism** (emit code, test it, feed the error back to the same AI so it isn't repeated) converges with Self-Refine (Madaan et al., 2023) and Reflexion (Shinn et al., 2023). **The cost asymmetry between phases** (a free AI for many iterations in Phase 1, an expensive AI for one rigorous pass in Phase 2) converges with the model-cascade logic described in FrugalGPT (Chen, Zaharia & Zou, 2023).

**Phase 2's budget constraint** (every action targeted, not exploratory) converges with Wu et al. (2026), who formalize the same principle for long-horizon search agents as a sequential decision problem constrained by an explicit context budget. **The reload gap** converges with the thread on self-governing context (Self-GC) and on agents that treat their own context state as an observable signal ("LLM Agents Are Latent Context Managers").

**The separation of phases** resonates with Mei et al.'s (2025) distinction among the foundational components of Context Engineering — retrieval, generation, processing, management — and in particular with the "just-in-time context" principle for external tool integration in an agentic architecture.

---

## 9. Limitations

This document is an *overview*, not a controlled study, and should be read as such.

1. **N = 1.** The architecture emerged from a single project. There is no comparison with a control group, nor with an alternative architecture applied to the same project. Claims about the architecture's properties are claims about *this* instance, not about a class.

2. **The case study is a single instance.** The reload gap is a concrete failure mode, but it is a single case. The generalization to the principle "a static instruction only constrains at the triggers it names" is supported by convergence with the literature (Section 8), not by an experiment.

3. **No comparative measure.** There are no baselines, no efficiency or quality metrics that can be compared. The "1.6x" reported in Section 4 is from Wu et al. (2026), not ours. The CI numbers (Section 6.8) are a scale datum, not a measure of the method's effectiveness.

4. **The 2026 references are preprints**, not peer-reviewed at the time of writing, and are cited with that caveat. The convergences declared in Section 8 were verified after the fact and do not constitute a theoretical derivation.

5. **Model names are contingent.** DeepSeek, Opus 5, and Claude Code are the models used in this project's practice at the time of writing. The structural properties the document assumes (context window, per-iteration cost, agentic behavior) may change between versions and between models, and the claims should be read as relative to this configuration, not as universal properties.

6. **Phase 1 is described more synthetically than Phases 2–4**, and this reflects the documentation asymmetry discussed in Section 7.1. It is not a presentation choice: it is a property of the architecture, but it makes Phase 1 less externally verifiable than the subsequent phases.

7. **The process/constraint distinction (Section 7.3) has not been validated.** We did not find explicit formulations in the literature we surveyed, but this does not mean they do not exist in literature we did not consult. We present it as an observation, not as a result.

---

## 10. Conclusion

The strength of the architecture does not come from the isolated use of any one particular AI. It comes from the **separation of responsibilities.** Each phase has its own environment, function, type of knowledge, success criterion, and set of controls.

The general principle can therefore be formalized as:

> **Intuition → Exploration → Verification → Discovery → Industrialization → new observation → new intuition.**

Artificial intelligence thus becomes a **multiplier of the human research process**, not necessarily a substitute for the initial act of imagination. The human side generates the direction. The AIs amplify the ability to explore it. The papers supply the scientific reference. The RAG keeps the connection to the sources. Discovery builds the public memory. The tests supply independent checks. CI and the guardrails prevent known errors from passing undisturbed through the pipeline. Production, finally, turns the experimental result into a stable software component.

The result, then, is not simply a program generated by an AI. It is the product of a pipeline in which intuition, scientific knowledge, artificial intelligence, experimentation, verification, and software engineering are deliberately kept separate and then recomposed into a single research process.

Two observations close the document. First, the asymmetric documentation of the architecture — light in Phase 1, dense in Phases 2–4 — is not a gap but a property: it reflects the fact that the success criterion changes at every transition, and that documenting has a cost justified only where the criterion is convergent and verifiable. Second, models are not interchangeable components: each phase assumes specific structural capabilities, and model choice is part of the method. The reload gap, finally, remains as an operational reminder: a static instruction only constrains behavior at the specific trigger points it names, and coverage is verified by tracing every path that produces the failure state, not only the one that was in mind when the instruction was written.

---

## Companion documents

This document is an overview. The operational details live in the companion documents below; read the one that matches your role.

| Document | Addressee | Purpose |
|---|---|---|
| [`draft_verification_methodology.md`](draft_verification_methodology.md) | Human researcher | Workflows 1 and 2 — the Draft/Review two-phase structure, in full |
| [`operational_constraints.md`](operational_constraints.md) | AI agent | The standing rule module reloaded at bootstrap |
| [`context_engineering_case_study.md`](context_engineering_case_study.md) | Both | The reload gap as a standalone case study |
| [`verification_layers.md`](verification_layers.md) | Human researcher | Workflows 3 and 4 — Discovery and Evolving Software repositories, in full |

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
