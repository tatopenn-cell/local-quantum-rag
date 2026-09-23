# Constraint Activation in Multi-Turn LLM Agent Sessions: A Case Study

**Field:** Context Engineering (Mei et al., 2025) / LLMOps — the operational discipline of managing what information, in what form, reaches a large language model at inference time, distinct from data science (statistical inference over datasets).

## Abstract

Standing behavioral constraints for an LLM coding agent — token-budget discipline, tool-specific conventions, cross-session memory — are typically encoded once, as a static instruction set, and assumed to remain in effect for the lifetime of a session. This case study documents a concrete failure mode of that assumption: a fixed instruction to reload a rule set was scoped only to conversation compaction events, leaving a real gap at plain session start. We report the incident, the fix, and situate both within the broader Context Engineering literature on budget-aware and self-governing context management.

## 1. Background

Context Engineering, formalized as a distinct discipline by Mei et al. (2025) in a survey drawing on over 1,400 papers, treats the systematic construction of an LLM's input context — not prompt wording alone — as the primary lever on agent behavior. The survey identifies context *management* (what persists, what is dropped, what is reloaded) as one of its foundational components, alongside retrieval, generation, and processing.

A specific sub-problem within context management is budget-aware operation under a finite token window. Wu et al. (2026) frame this as a sequential decision problem with an explicit context-budget constraint (`ContextBudget` / BACM), reporting throughput gains of over 1.6x versus unconstrained baselines in high-complexity, long-horizon settings by learning *when* to compress rather than compressing uniformly. Related work on self-governing context (Self-GC) and on agents that treat their own context state as an observable signal ("LLM Agents Are Latent Context Managers") converges on the same finding: an agent's operating rules must be actively re-asserted at defined trigger points, not assumed to persist by default once written down.

## 2. The system under study

The agent in this case study operates under a layered constraint system:

1. A fixed, always-in-force instruction, stored outside the conversation (`CLAUDE.md`), naming *when* to reload the operating rule set.
2. A skill file (`session-rules`) containing the actual rule content: token-economy discipline (nine numbered rules — avoid redundant reads, batch independent tool calls, prefer targeted edits over full-file rewrites, avoid unnecessary sub-agent chains, and a rule prioritizing real compute/energy cost over token cost specifically) and a project-specific documentation style guide (sixteen numbered rules).
3. A cross-session memory store (~35 entries at time of writing), consulted contextually rather than reloaded in full each turn.
4. Tool-specific conventions that activate only while a given tool (version control, a publishing surface, a documentation-lookup service) is actually in use during a turn.

Layers 2 and 4 are not part of the model's persistent weights or default context — each is either invoked explicitly (layer 2) or supplied by the tool integration itself at call time (layer 4).

## 3. The incident

The fixed instruction (layer 1) read: reload the rule set "after every `/compact`" — `/compact` being the operator that summarizes a long conversation to free context space. This correctly anticipates one real failure mode: a summarization pass drops the literal rule text while preserving only a reference to its existence, so the rule content must be explicitly reloaded afterward.

It did not anticipate a second, functionally identical failure mode: a session that begins fresh (no prior compaction in its own history) never triggers the instruction at all, since no `/compact` event has yet occurred. The rule file exists on disk in both cases; in neither case does its existence alone place its content into the model's active context. The two triggers are not distinct problems requiring separate handling — they are the same event (loss of, or absence of, a fully-loaded rule context) reached by two different paths.

## 4. Fix and verification

The fixed instruction was revised to name both trigger conditions explicitly: session start, in addition to post-compaction. Verification consisted of invoking the rule-reload skill immediately after the edit, confirming it executes at the point of failure previously left uncovered, and cross-checking the skill file itself for completeness against the rule content it was meant to reproduce verbatim (found to already be complete and current at the time of this fix).

## 5. Discussion

This incident is a small, concrete instance of the general finding in the budget-aware and self-governing context literature above: a static instruction, however correctly written, only constrains behavior at the specific trigger points it names. Coverage gaps are found by tracing *every* path that produces the failure state the instruction was meant to prevent (here: an under-loaded rule context), not only the path that was top of mind when the instruction was first written. The fix required no new mechanism — only widening an existing trigger condition to match the actual failure surface.

## References

1. L. Mei, J. Yao, Y. Ge, Y. Wang, B. Bi, Y. Cai, J. Liu, M. Li, Z.-Z. Li, D. Zhang, C. Zhou, J. Mao, T. Xia, J. Guo, S. Liu, *A Survey of Context Engineering for Large Language Models*, arXiv:2507.13334 (2025).
2. Y. Wu, Y. Zheng, T. Xu, Z. Zhang, Y. Yu, J. Zhu, C. Ma, B. Lin, B. Dong, H. Zhu, R. Huang, G. Yu, *ContextBudget: Budget-Aware Context Management for Long-Horizon Search Agents*, arXiv:2604.01664 (2026).
3. *Self-GC: Self-Governing Context for Long-Horizon LLM Agents*, arXiv:2607.00692 (2026).
4. *LLM Agents Are Latent Context Managers: Eliciting Self-Managed Context via a Proprioceptive Dashboard*, arXiv:2606.30005 (2026).
