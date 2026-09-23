# Draft and Verification: a Two-Phase Structure for AI-Assisted Development

**Nature of this document**: this is a **process** document, not a constraint document. It describes how a human researcher organizes their own work over time, using multiple AI assistants in different roles. It is not addressed to an AI and should not be handed to an AI as an operating instruction: an assistant reading it as a rule would try to execute "phase 1 then phase 2" on itself, which makes no sense — the two phases are carried out by two *different* AIs, deliberately chosen for opposite roles. The companion document, distinct and separate, is the **constraints** document (`operational_constraints.md`): that one *is* addressed to an AI.

---

## Premise: two phases, not two grades of the same work

The process splits into a **divergent** phase (the draft) and a **convergent** phase (the review). These are not the same activity done with more or less care: they have opposite goals, tools, and success criteria, and mixing them produces a worse result than either taken alone.

## Phase 1 — The Draft (divergent phase)

**Goal**: explore. Understand a paper's logic, translate it into code, see whether the idea holds up — without yet having to defend it all the way through.

**Tool**: a free AI with a very large context window (on the order of a million tokens) — in current practice, DeepSeek's free tier. The choice isn't incidental: this phase can require many repetitions, so it runs on a tool whose per-iteration cost is close to zero.

**Procedure**:
1. Load the original papers into the AI.
2. Build an understanding of the paper's logic together with the AI.
3. Have the AI emit the corresponding code.
4. Copy that code by hand and run it in an external test environment (Kaggle or Colab) — execution happens outside the session that generated the code.
5. When a bug shows up, the fix goes back to the same "primary" AI for this phase, not treated as a side note: this way the AI has already dealt with that error by the next attempt and doesn't repeat it. Debugging is followed and pasted in by hand, never delegated blindly.

**Exit criterion**: the draft counts as complete **only** once it stops behaving like a draft — every test passes, every calculation has actually run and reached a concrete result. At that point it is treated as a finished project, not a sketch to be polished later.

**Note**: it happens that the draft's quality exceeds that of the subsequent review phase — that's a sign the brainstorming worked well, not an anomaly to correct.

**Required mindset**: during this phase, the human must also forget that a review phase will follow. Knowing in advance that another AI will "check everything afterward" lowers one's guard and produces a less rigorous draft — exactly the opposite of what's needed, since the review phase assumes the draft is already the best possible version, not a sketch to be corrected. The draft must be carried out as if it were the only, final chance: work any other way, and the draft simply doesn't work.

## Phase 2 — The Review (convergent phase)

**Goal**: apply, not explore. No more brainstorming here.

**Tool**: a strong local AI, with real access to the source papers via RAG (quantum-rag), handed the already-complete draft — the best version phase 1 could produce — together with the working code.

**Task**: debug and enforce every constraint from the constraints framework, within its own token budget, and check whether the draft actually honored every point described in the source text — not redesign it. This phase *is* the real project: it's where every operating rule actually gets applied.

**When the numbers don't add up**: dig into why and where, and log the failure so it isn't repeated — the same principle as phase 1, applied at phase 2's standard of rigor.

**Tool for code**: only a strong, paid-tier AI (Claude Code or an equivalent level). The one non-negotiable rule of this phase: the AI never proceeds on its own initiative — one point at a time, in order, never beyond what's asked.

---

## Which literature this converges with

The method described here arose empirically — it was not derived from the works below. The correspondence was verified after the fact, not used as a starting foundation; it should be read as a framing, not a pre-existing theoretical basis.

**The two-phase structure as a whole** matches the distinction between *divergent* and *convergent* thinking introduced by Guilford in his structure-of-intellect model (Guilford, 1956), and operationalized as a two-phase process by the UK Design Council's "Double Diamond" model (Design Council UK, 2005): a phase that generates and explores possibilities (*discover*), followed by a phase that evaluates, selects, and refines (*define*) — precisely the relationship between Draft and Review described here.

**Phase 1's internal mechanism** (emit code, test it, feed the error back to the same AI so it isn't repeated) converges with two recent threads in LLM-agent research: Self-Refine (Madaan et al., 2023), where the same LLM generates an output, critiques it, and refines it iteratively with no extra training required; and Reflexion (Shinn et al., 2023), where the agent doesn't update its own weights but keeps a textual memory of past failures to avoid repeating them on later attempts — the exact principle behind "the debug is followed and pasted in by hand, so the AI has already dealt with it by the next attempt."

**The cost asymmetry between the two phases** (a free AI for many iterations, an expensive AI for one final, rigorous pass) converges with the model-cascade logic described in FrugalGPT (Chen, Zaharia & Zou, 2023): use a cheap model for the bulk of exploratory work and reserve the expensive model for the pass that actually matters, reaching the same result — or better — at a fraction of the cost.

## References

1. J. P. Guilford, *The Structure of Intellect*, Psychological Bulletin, Technical Report 4 (1956).
2. Design Council (UK), *Eleven Lessons: A Study of the Design Process — The Double Diamond* (2005).
3. A. Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, arXiv:2303.17651 (2023).
4. N. Shinn, F. Cassano, E. Berman, A. Gopinath, K. Narasimhan, S. Yao, *Reflexion: Language Agents with Verbal Reinforcement Learning*, arXiv:2303.11366, NeurIPS 2023.
5. L. Chen, M. Zaharia, J. Zou, *FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance*, arXiv:2305.05176 (2023).

---

## Why the two phases must not be mixed

An AI asked simultaneously to "explore freely" and to "rigidly follow every constraint" receives a contradictory instruction — it cannot tell which behavior to prioritize, and the result is a hybrid that does neither well. This is why the structural theory (this document) stays out of the constraints theory: an AI in the review phase must never read "first, free brainstorming" as if it applied to itself.
