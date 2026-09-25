# Methodological Architecture in Four Phases

## From Intuition to Scientific Discovery and Production Software

The methodology can be reorganized into **four distinct operational phases**, each with its own goal, environment, tools, advancement criteria, and control mechanisms.

The fundamental point is that the four phases **are not interchangeable**: each one solves a different problem.

---

# General Schema

```text
                 ┌──────────────────────────┐
                 │  HUMAN INTUITION         │
                 │  Interest / analogy      │
                 │  hypothesis / question   │
                 └────────────┬─────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 1 — EXPLORATION AND IMPLEMENTATION                │
│ DeepSeek + Google AI for search                          │
│                                                          │
│ Idea → literature → context → code → experiment         │
│ → debugging → prototype                                  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 2 — SCIENTIFIC VERIFICATION                        │
│ Opus 5 + local-quantum-rag                                │
│                                                          │
│ Code → paper → mathematics → verification → cross-check │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 3 — DISCOVERY                                       │
│ Public environment / GitHub                              │
│                                                          │
│ Documentation → experiments → tests → reproducibility   │
│ → coverage → shared memory → validation                  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ PHASE 4 — SOFTWARE / PRODUCTION                          │
│ Real library                                              │
│                                                          │
│ Integration → API → tests → CI → compatibility           │
│ → guardrails → release                                    │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
                    NEW RESULTS
                           │
                           ▼
                    NEW INTUITION
```

---

# PHASE 1 — EXPLORATION AND IMPLEMENTATION

## DeepSeek: turning an intuition into a working prototype

### Goal

The first phase exists to turn an **intuitive direction** into a concrete computational object.

There is no claim yet to definitively prove the idea's scientific correctness.

The main question is:

> **"Can we turn this intuition into a working experiment?"**

---

## 1. The human trigger

The process starts from the operator's own interest.

The trigger can be:

* a documentary;
* an image;
* a theory;
* a formula;
* something read;
* an observed problem;
* a personal experience;
* a random association;
* a passion;
* an apparently naive question.

The Minkowski diagram example is representative: observing a geometric structure can generate the idea of relating it to an already-studied quantum problem.

It is not yet a theory.

It is a **direction to explore**.

---

## 2. Attention and curiosity

The intuition requires attention.

The operator must be sufficiently engaged with the problem to recognize relationships that were not explicitly being searched for.

In this phase:

**interest → attention → association → hypothesis.**

An error is not a methodological failure.

A hypothesis can be discarded.

---

## 3. First experiment

The first idea is quickly turned into a sketch or a small implementation.

If the result produces nothing, the hypothesis is modified or abandoned.

The principle is:

> **first check experimentally whether something exists at all, then invest further in the direction that shows potential.**

---

## 4. Brainstorming with the AI

The conversational AI is used as a processing space.

The goal is not necessarily to obtain the solution immediately.

The conversation serves to:

* make the idea explicit;
* formulate questions;
* identify possible connections;
* generate hypotheses;
* identify problems;
* turn vague intuitions into technical questions.

The AI thus becomes an **amplifier of the exploratory process**.

---

## 5. State-of-the-art search

Before seriously implementing a new idea, a literature search is carried out.

What is searched for:

* original papers;
* recent work;
* related algorithms;
* existing implementations;
* results already obtained;
* known limitations.

The purpose is to avoid presenting as new an idea that has already been studied.

---

## 6. Gathering papers

The relevant scientific documents are downloaded and organized.

The user does not necessarily need to study all of them in depth immediately.

The initial phase mainly consists of building a **document map of the problem**.

The papers become operational material for the AIs.

---

## 7. Building DeepSeek's context

DeepSeek receives a context made up of:

* existing code;
* architecture;
* the project's style;
* papers;
* documentation;
* previous results;
* the idea to implement;
* the experimental goal.

The problem is thus transformed from:

> "Write an algorithm."

into:

> **"Integrate this new scientific idea into this specific software system."**

---

## 8. The limit of the AI as information

When DeepSeek runs into a difficulty, the response is not simply to force it to keep going.

The question asked is:

> **"What is missing for you to be able to answer?"**

The model can identify:

* mathematical knowledge;
* papers;
* formulas;
* techniques;
* references;
* contextual information.

These gaps become new research tasks.

---

## 9. Orchestration across multiple AIs

Difficult questions can be handed off to another system.

For example:

```text
DeepSeek
   ↓
unresolved question
   ↓
Google AI / another AI
   ↓
partial answer
   ↓
new questions
   ↓
additional papers
   ↓
DeepSeek
```

This way, one model's limit becomes the input for the next one.

---

## 10. Implementation

Once the context is sufficient, DeepSeek generates the code.

The implementation can include:

* new functions;
* new modules;
* new algorithms;
* new applications;
* new tools;
* integrations with the existing library.

These are not necessarily small changes.

A single idea can produce a significant amount of new code.

---

## 11. Experimental execution

The code is run, for example, in Google Colab.

The experimental environment makes it possible to keep separate:

**exploratory code**

from

**production software**.

The results are then concretely observed.

---

## 12. Iterative debugging

When an error appears:

```text
Code
 ↓
Execution
 ↓
Error
 ↓
Output / traceback
 ↓
DeepSeek
 ↓
Fix
 ↓
New execution
```

The cycle can repeat many times.

Debugging becomes an integral part of the methodology.

---

### Output of Phase 1

The phase ends when there is a:

> **working experimental prototype, documented enough to be submitted to scientific verification.**

---

# PHASE 2 — SCIENTIFIC VERIFICATION

## Opus 5 + local-quantum-rag: from "does it work" to "is it scientifically correct?"

The second phase completely changes the success criterion.

The question is no longer:

> "Does the code work?"

but:

> **"Does the code actually implement what the scientific literature states?"**

---

## 13. Introducing local-quantum-rag

The original papers are organized inside the RAG system.

The RAG lets the model selectively retrieve the parts of the literature needed for verification.

Schema:

```text
Code
   ↓
verification question
   ↓
local-quantum-rag
   ↓
original paper
   ↓
relevant passage
   ↓
Opus 5
   ↓
verification
```

---

## 14. Formal verification

Opus 5 analyzes the relationship between:

* formula;
* definition;
* algorithm;
* implementation;
* result.

The goal is to establish correspondence between the code and the scientific source.

---

## 15. Mathematical verification

What gets analyzed:

* formulas;
* metrics;
* transformations;
* conditions;
* assumptions;
* parameters;
* edge cases.

This is the phase in which conceptual knowledge is turned into formal verification.

---

## 16. Point-by-point check

The code is compared against the paper systematically.

Ideally:

```text
Paper
 ↓
definition
 ↓
formula
 ↓
algorithm
 ↓
implementation
 ↓
output
```

Each step must be consistent with the next.

---

## 17. Independent verification

The result is compared against:

* reference implementations;
* known results;
* analytical formulas;
* independent applications;
* benchmarks.

The goal is to prevent an internal error from being mistaken for a valid result.

---

### Output of Phase 2

The result is a:

> **scientifically verified implementation, explicitly connected to the reference literature.**

---

# PHASE 3 — DISCOVERY

## Public environment: turning the result into reproducible knowledge

This is the phase that must be kept conceptually separate from the first two.

**Discovery is not brainstorming.**

It is the environment in which new experimental knowledge is made public, checkable, and shareable.

---

## 18. Moving into the Discovery space

The project is brought into the public environment, typically GitHub.

Here the rule system changes.

The code is no longer simply:

> "something that works on my computer."

It becomes:

> **"something that must be able to be examined by others."**

---

## 19. Rules specific to this environment

The Discovery layer contains dedicated instructions covering:

* documentation;
* experiments;
* tests;
* claims;
* coverage;
* reproducibility;
* project structure;
* verification methodology.

The rules are not simply contained in the AI's prompt.

They are embedded in the environment.

---

## 20. Documentation

Every result must be reconstructible.

The documentation links:

```text
Idea
 ↓
Paper
 ↓
Method
 ↓
Code
 ↓
Experiment
 ↓
Result
```

This creates a persistent memory.

---

## 21. Shared human-AI memory

The documentation has a second function.

It becomes a memory that can be consulted by:

* the author;
* collaborators;
* other AIs;
* reviewers;
* future developers.

A different AI can be tasked with reading a GitHub page and looking for errors.

The repository thus becomes a **shared-memory substrate**.

---

## 22. Transparency of the AI's own work

The documentation makes it possible to check whether the system actually understood its own work.

The AI must be able to explain:

* what it implemented;
* why;
* from which paper;
* which formula it uses;
* how it was verified;
* what the limitations are.

---

## 23. Reproducible experiments

Experiments must be repeatable.

What must be defined:

* conditions;
* inputs;
* parameters;
* environment;
* expected outputs;
* metrics;
* success criteria.

The discovery is thus turned from a personal experience into a **reproducible object**.

---

## 24. Scientifically meaningful tests

Tests must not be limited to trivial cases.

They must also check:

* edge cases;
* properties;
* known results;
* expected behavior;
* numerical stability;
* comparison against references.

---

## 25. Cross-validation

The result must match, when possible, an independent reference.

Schema:

```text
New implementation
        ↓
     result
        ↕
reference implementation
        ↓
     result
```

Agreement constitutes a further level of verification.

---

## 26. Discovery guardrails

The environment can automatically block progression when a condition is not met.

For example:

```text
test failed
     ↓
pipeline blocked
```

or:

```text
insufficient coverage
     ↓
change not accepted
```

This matters because the system must not depend solely on the AI's ability to remember every rule.

---

### Output of Phase 3

The phase produces:

> **a public, documented, reproducible result, tested and subjected to independent checks.**

---

# PHASE 4 — SOFTWARE / PRODUCTION

## Turning the discovery into robust software

The last phase is completely different from Discovery.

The question is no longer:

> "Is the experiment interesting?"

The question is:

> **"Can this new component stably enter a real software library?"**

---

## 27. Adapting the code

The experimental code is not necessarily carried over directly.

What may be needed:

* refactoring it;
* changing its API;
* adapting it to the architecture;
* removing experimental code;
* improving error handling;
* integrating dependencies;
* adding documentation.

---

## 28. Integration into the library

The new component must coexist with:

* pre-existing code;
* APIs;
* dependencies;
* versions;
* operating systems;
* other features.

The problem thus becomes systemic.

---

## 29. Regression tests

A new feature must not break what already worked.

The system must therefore check:

```text
new feature
      +
existing code
      ↓
no regression
```

---

## 30. CI and automation

The automated pipeline runs the checks without requiring a full manual review on every change.

This shifts the checking from the operator's memory to the machine.

---

## 31. Codecov and coverage

Coverage checks how much of the new and modified code is actually exercised by the tests.

It is not, by itself, proof of scientific correctness, but it is one of the engineering mechanisms that contribute to the product's robustness.

---

## 32. Cross-platform compatibility

The library is checked across multiple configurations.

In the case described here:

* 3 macOS environments;
* 3 Ubuntu environments;
* around 1,344 tests per environment (verified against a real CI run).

Total:

**over 8,000 test executions.**

This reduces the risk that a change only works in the author's own environment.

---

## 33. Production guardrails

The principle is:

> **if a critical condition is not met, the release does not proceed.**

For example:

```text
Tests failed
     ↓
PUSH BLOCKED
```

or:

```text
Insufficient coverage
     ↓
PUSH BLOCKED
```

Guardrails thus turn rules from recommendations into **operational constraints**.

---

## 34. Release

Only after the pipeline is passed can the new component be included in the production software.

At this point the path is:

```text
Intuition
   ↓
Experiment
   ↓
Scientific verification
   ↓
Public Discovery
   ↓
Integration
   ↓
CI / Tests / Coverage
   ↓
Release
```

---

# 35. The role of the four phases

| Phase | Environment | Main question | Output |
|---|---|---|---|
| **1. Exploration** | DeepSeek | Can we turn the idea into an experiment? | Prototype |
| **2. Verification** | Opus 5 + local-quantum-rag | Does the prototype correctly implement the science? | Verified implementation |
| **3. Discovery** | GitHub / public environment | Can we document and reproduce the result? | Public, reproducible result |
| **4. Production** | Library / CI | Can we integrate it without breaking the software? | Release |

---

# 36. The four levels of control

The complete structure can also be read as a progression of four kinds of control:

### Level 1 — Experimental control

**Does it work?**

### Level 2 — Scientific control

**Is it correct with respect to theory and the literature?**

### Level 3 — Epistemic control

**Is it documented, reproducible, and checkable by others?**

### Level 4 — Engineering control

**Is it stable, integrable, and maintainable in real software?**

These four controls are not equivalent.

A program can work but be scientifically wrong.

It can be scientifically correct but poorly documented.

It can be scientifically correct and well documented but break the library.

The methodology exists precisely because of the need to **not conflate these four problems**.

---

# 37. The full cycle

The entire method can be represented in its most compact form:

```text
                         HUMAN
                          │
             intuition / attention
                          │
                          ▼
              ┌─────────────────────┐
              │ PHASE 1             │
              │ DEEPSEEK            │
              │                     │
              │ idea → code         │
              │ → experiment        │
              │ → debugging         │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ PHASE 2             │
              │ OPUS 5 + RAG        │
              │                     │
              │ code ↔ paper        │
              │ mathematics         │
              │ verification        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ PHASE 3             │
              │ DISCOVERY           │
              │                     │
              │ documentation       │
              │ tests               │
              │ reproducibility     │
              │ cross-validation    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ PHASE 4             │
              │ SOFTWARE            │
              │                     │
              │ integration         │
              │ CI                  │
              │ coverage            │
              │ compatibility       │
              │ release             │
              └──────────┬──────────┘
                         │
                         ▼
                   NEW RESULT
                         │
                         ▼
                  NEW OBSERVATION
                         │
                         ▼
                  NEW INTUITION
```

---

# 38. Concluding architectural principle

The strength of the methodology does not come from the isolated use of any one particular AI.

It comes from **separation of responsibilities**.

Each phase has:

* an environment;
* a function;
* a kind of knowledge;
* a success criterion;
* a set of controls.

The general principle can therefore be formalized as:

> **Intuition → Exploration → Verification → Discovery → Industrialization → new observation → new intuition.**

Artificial intelligence thus becomes a **multiplier of the human research process**, not necessarily a substitute for the initial act of imagination.

The human side generates the direction.

The AIs amplify the ability to explore it.

The papers supply the scientific reference.

The RAG keeps the connection to the sources.

Discovery builds the public memory.

The tests supply independent checks.

CI and the guardrails prevent known errors from passing undisturbed through the pipeline.

Production, finally, turns the experimental result into a stable software component.

**The result, then, is not simply a program generated by an AI. It is the product of a pipeline in which intuition, scientific knowledge, artificial intelligence, experimentation, verification, and software engineering are deliberately kept separate and then recomposed into a single research process.**
