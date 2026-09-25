# One Well-Constrained Task Substitutes for a Thousand Unverified Ones: Accumulated Specific Constraints as an Alternative to Unverified Agentic Parallelism

**Status**: working draft, case-study paper. Every citation below has been checked against its real source before inclusion. Every case study is drawn from two public, existing repositories (`local-quantum-rag`, `Dense-Evolution`/`Dense-Evolution-Discovery`) and from this draft's own preparation — nothing here is a synthetic or hypothetical example. No quantitative efficiency ratio is claimed; see the explicit limitation in Section 5.

## Abstract

A common response to the unreliability of a single LLM agent is to add more agents — parallel drafts, majority voting, swarms of independently-acting instances. We report a contrary pattern observed across two independent open-source projects: a single agent operating under a growing set of specific, human-authored, non-generalized constraints — each one distilled from one concrete, verified failure — substitutes for the error-catching that unverified parallelism is meant to provide, without multiplying inference cost by the number of agents. We ground the underlying premise (more specific information improves task performance) in the retrieval-augmented generation literature, situate the accumulation mechanism in the Case-Based Reasoning tradition and in the regression-test-suite practice of software engineering, formalize the pipeline this mechanism operates inside as four phases answering four independently-failable questions (Boehm's verification/validation distinction, extended here with reproducibility and integration as two further checks neither verification nor validation alone covers), and report three case studies — one previously published as an independent case study, two newly reported here — in which a concrete failure was converted into exactly one permanent, specific artifact rather than a generalized rule. We discuss what does and does not generalize in this mechanism, and state plainly that this is a case-study report, not a controlled quantitative comparison against a multi-agent baseline.

## 1. Introduction

It is well established that a language model conditioned on specific, relevant, retrieved information outperforms the same model working from parametric memory alone on knowledge-intensive tasks (Lewis et al., 2020); the retrieval component itself is typically a dense encoder trained to surface exactly the passages a query needs (Karpukhin et al., 2020). This is the premise this paper starts from, and it is not itself a contribution — it is decades of established retrieval and in-context-learning literature.

The open question this paper addresses is narrower: information alone does not tell an agent *when* a given signal or correction should be trusted. A signal can be informative in one role and actively misleading in another, in the same codebase, produced by the same underlying computation (Section 4.2). Supplying more information does not resolve this; only verification does. This raises a resource question: does resolving it require more agents working in parallel — so that errors are caught by redundancy or by vote — or does it require something else?

We report evidence for something else: a single agent, executing under constraints that were themselves derived one at a time from specific, verified failures, catches the same class of error that unverified parallelism is meant to catch, and does so by accumulation rather than by multiplication. We call the accumulated set of these constraints, deliberately, a **castle** rather than a **framework** — a framework implies a generalized, reusable structure; a castle is built stone by stone, each stone shaped for the specific gap it fills, and the load-bearing property of the whole depends on the stones staying particular, not on any one of them being generalized into a rule that covers cases it was never actually tested against.

## 2. Related Work

**Context Engineering.** Mei et al. (2025) formalize, across a survey of over 1,400 papers, the discipline of constructing an LLM's input context — not prompt wording alone — as the primary lever on agent behavior, identifying context *management* (what persists, what is dropped, what is reloaded) as a foundational component alongside retrieval, generation, and processing.

**Budget-aware and self-governing context.** Wu et al. (2026) frame long-horizon agent operation as a sequential decision problem under an explicit context-budget constraint, reporting throughput gains of over 1.6× against unconstrained baselines by learning *when* to compress rather than compressing uniformly. Related work on self-governing context (Self-GC, 2026) and on agents that treat their own context state as an observable signal (*LLM Agents Are Latent Context Managers*, 2026) converges on the same finding relevant here: an agent's operating constraints must be actively re-asserted at defined points, not assumed to persist once written down.

**Case-Based Reasoning.** Aamodt and Plaza (1994) formalize problem-solving by retrieving and adapting specific prior cases, rather than by applying a generalized rule derived from them — the theoretical basis for treating each verified failure in this paper as a retained, particular case rather than an instance to be abstracted away.

**Iterative self-correction.** Self-Refine (Madaan et al., 2023) has an LLM critique and revise its own output iteratively with no additional training; Reflexion (Shinn et al., 2023) keeps a textual memory of an agent's own past failures specifically to avoid repeating them on later attempts. Both converge on the same operational principle used in Section 4's case studies: a failure, once observed, is not discarded but converted into memory that changes future behavior on that specific case.

**Cost asymmetry across a pipeline.** FrugalGPT (Chen, Zaharia and Zou, 2023) shows that cascading a cheap model for the bulk of exploratory work with an expensive model reserved for the one pass that actually matters reaches equal or better results at a fraction of the cost of running the expensive model throughout. This motivates concentrating verification effort at one well-chosen point rather than distributing it evenly, or multiplying it, across many unverified attempts.

**Divergent and convergent phases.** Guilford's structure-of-intellect model (1956) distinguishes divergent thinking (generating possibilities) from convergent thinking (evaluating and selecting among them); the UK Design Council's Double Diamond model (2005) operationalizes the same distinction as two sequential phases, *discover* and *define*. Both provide the structural basis for keeping exploration and verification as separate phases with opposite goals, rather than one blended activity — a distinction load-bearing in Section 4.1's case study, where the two phases are explicitly assigned to different tools.

## 3. Mechanism: The Constraint Castle

We define a constraint castle as the accumulated set of specific, human-authored constraints, each one derived from exactly one verified failure, retained without being generalized beyond the failure that produced it.

Two existing traditions justify why this remains effective as it grows, and why the correct operation is accumulation rather than abstraction:

1. **Case-Based Reasoning** (Aamodt and Plaza, 1994) treats each retained case as valid within the boundary of its own similarity to a new situation, not as evidence for a universal law. This matches the failures reported in Section 4 directly: a fix that is correct for one specific gap (Section 4.1's missing trigger path; Section 4.2's two specific misuses of a divergence signal) would be actively wrong if generalized past its boundary — the same divergence signal that fails as a continuous correction weight in two contexts remains correct and load-bearing as a threshold decision in a third, in the same codebase (Section 4.2).
2. **Regression testing**, as practiced in software engineering, converts each discovered defect into exactly one permanent, specific test, never a generalized rule about defects of that shape in general. The suite's coverage accumulates monotonically; the marginal cost of not repeating a specific past mistake drops to near zero, without ever requiring the codebase to run redundant, independently-acting checks against the same defect in parallel.

The substitution claim follows from combining the two: an agent operating inside a growing, specific constraint castle catches the same class of error that unverified parallel agents are meant to catch via redundancy or voting, because the castle already encodes, as retained cases, the specific failures a swarm would otherwise have to rediscover independently and unreliably, in every member, every time.

### 3.1 Why Constraints Must Be Co-Authored, Not Inferred

Polanyi (1966) describes tacit knowledge as knowledge its holder cannot fully articulate — "we know more than we can tell" — and that therefore cannot be recovered by an outside observer no matter how closely that observer examines the visible artifact alone. This bears directly on the castle described above: a constraint derived only from what is externally observable (a bug, a missing test, a broken link) is necessarily incomplete, because part of what makes a specific working method fast and effective is exactly this tacit component — preferences, shortcuts, and judgment calls an AI assistant has no independent channel to discover, however capable it is at pattern-matching over the artifact in front of it.

This clarifies the division of labor implied by Section 3: an AI assistant executes reliably once a constraint has been stated explicitly, and can surface candidate failures for a human to judge, but the constraint's content is co-authored — its strength depends on tacit, personal knowledge that only the human contributes, and that no amount of inference from the artifact alone recovers.

This also clarifies where each party's comparative advantage lies. A coding-oriented AI assistant is not the same model, nor tuned for the same objective, as a general conversational AI, even when both are accessed through the same product or session: the former is reliable at executing against a goal that has already been made fully specific and ready to act on, not at open-ended understanding of an underspecified goal or at deciding what that goal should be — a different model's role, tuned for a different objective. This is consistent with the constraint castle's own division of labor (Section 3): the human's contribution is preparing the specific, ready target in advance; the coding assistant's contribution is executing and debugging against it reliably, not inventing what it should be or standing in for a conversational model's role.

### 3.2 A Four-Phase Pipeline and Four Levels of Control

The castle mechanism described above operates inside a larger pipeline, structured as four phases with four distinct success criteria — not four names for the same activity done with varying care, but four different questions, each answerable only by its own phase:

1. **Exploration** ("can this intuition become a working experiment?") — a divergent, low-cost phase run on a free-tier, large-context model, corresponding to the divergent pole of Guilford's (1956) and the Double Diamond's (Design Council UK, 2005) structure-of-intellect distinction already cited in Section 2.
2. **Verification** ("does the experiment actually implement what the literature states?") — a convergent phase run against the project's own retrieval system.
3. **Discovery** ("can the result be documented and reproduced by someone else?") — the phase in which a verified result is written up publicly, with its own repository, its own failed attempts kept in rather than discarded, and its own accumulation into the constraint castle of Section 3.
4. **Production** ("can it be integrated without breaking the software real users depend on?") — the phase in which only what survives Discovery reaches a published package, under the platform-enforced guarantees described in Section 4.3's packaging incident below.

This four-way split is a specific instance of a general principle already named in software engineering: Boehm (1984) separates *verification* ("are we building the product right?") from *validation* ("are we building the right product?") specifically because a system can satisfy one while failing the other. The pipeline here adds two further, independently failable questions on top of that pair — can the result be reproduced by someone outside the process (Discovery), and can it be integrated without regressing anything that already worked (Production) — because this project's own history (Section 4) shows failures at each of the four points independently: an idea that worked but was scientifically ungrounded, a scientifically sound result no one else could reproduce, and a fully verified, fully documented change that still broke a real installation once shipped (Section 4.3). Treating any one of these four checks as a stand-in for the others is exactly the failure mode Section 5 discusses under "conflating 'every test passed' with 'this is correct.'"

## 4. Case Studies

All three case studies below are drawn from real, existing repositories, not constructed for this paper. Case 4.1 was published independently, as its own case-study document, before this paper was drafted.

### 4.1 The Reload Gap (`local-quantum-rag`)

A fixed instruction governing an LLM coding agent read: reload its operating rule set "after every `/compact`" (the operator that summarizes a long conversation to free context space). This correctly covered one real failure mode — a summarization pass drops literal rule text while preserving only a reference to its existence. It did not cover a second, functionally identical failure mode: a session that begins fresh never triggers the instruction at all, since no `/compact` event has yet occurred in its own history. Both cases share the same underlying failure state (an under-loaded rule context) reached by two different paths.

The fix widened the existing trigger condition to name both paths explicitly. No new mechanism was introduced. The fix is permanent and specific to this exact failure surface; it does not generalize into, for instance, a rule about reloading arbitrary state at arbitrary intervals — doing so would have addressed a problem that was never observed. (Full report: `docs/context_engineering_case_study.md`, `local-quantum-rag`.)

### 4.2 The Jensen-Shannon-divergence gate/weight boundary (`Dense-Armor`, `Dense-Evolution-Discovery`)

The same class of signal — Jensen-Shannon divergence (JSD) between two probability distributions derived from a quantum circuit's or a monitored signal's state — was tested in three independent contexts within the same code ecosystem:

1. As a **threshold/gate decision** in an anomaly detector (`Dense-Armor`'s pressure-valve filter): JSD between a local and a reference window widens the anomaly threshold specifically near genuine regime transitions (verified: threshold ≈8.3 on stationary noise versus ≈8.7–8.8 near a real transition). This use remains in production, unmodified.
2. As a **continuous correction weight** scaling the magnitude of a zero-noise-extrapolation correction (`jsd_zne_oscillating_noise.py`): a permutation test against a shuffled-noise negative control found the JSD-weighted correction statistically indistinguishable from noise (significant in 0 to 1 of 11 tested configurations).
3. As a **continuous correction weight** in a second, independently-implemented mechanism (`zne_healing_sigma_provenance.py`, an empirical-sigma-based correction): the same negative-control test found the treatment statistically identical to a randomly shuffled version of itself (88.9% versus 86.7% win rate) — a confound, not a real effect. This mechanism was subsequently deprecated in the shipping library.

The two failures (2 and 3) were each resolved individually — one by not adopting the mechanism, one by a formal deprecation — and neither fix took the form of a general rule against using JSD, since case 1 demonstrates the same signal is correct and load-bearing elsewhere in the identical codebase (JSD also gates bond-dimension truncation in the library's matrix-product-state simulator, unrelated to either failure). A generalized rule derived from cases 2 and 3 alone ("do not use JSD-derived signals for correction") would have been directly contradicted by case 1.

### 4.3 Five specific gaps found and closed during this paper's own preparation

Within the working session that produced this draft, prior to any of the analysis above being written down, five independent, concrete gaps were found by direct execution rather than by assumption, each closed with exactly one specific, permanent artifact, on a single real pull request against the Dense-Evolution library (public repository, PyPI package):

- An optional-dependency code path (Hartree-Fock diagnostics requiring an extra package) had no test exercising its `ImportError` failure branch; one targeted test using dependency injection was added to cover exactly that branch.
- A numerical parameter on a newly added API endpoint (`beta`, a protocol-specific bound governing a device-independent quantum key distribution check) was documented as required (`0.75 < beta < 0.8536`) but not enforced in code, confirmed by direct execution (`beta=0.5` was silently accepted); the enforcement was added as a single explicit check at the point the gap was found, not deferred.
- A cross-reference between two documentation pages pointed at a page that had never been created; the reference was corrected in one line to point at the section that already contained the relevant content, rather than creating a redundant new page. Verified before and after with the exact command CI runs (`mkdocs build --strict`): failing before the fix, clean after.
- Two tools intended to expose identical functionality (`ia_utils.rag` and a standalone predecessor tool) were found, on direct comparison, to differ in one specific capability (exact-substring/regex search); the missing capability was ported as one function and covered by six new unit tests, each checked against the original tool's behavior line by line.

Patch coverage on the pull request carrying these changes moved from 89.28% (39 lines uncovered across 4 files) to 97.25% (10 lines uncovered) after an earlier round of 4 targeted tests, then to fully passing after the 2 tests above closed the remaining `ImportError` branches — each increment tied to one specific, identified gap, never a blanket rewrite. A fifth, unrelated failure on the same pull request (a full continuous-integration crash on one operating system) was traced to a single missing guard clause (`pytest.importorskip("sklearn")`) on the six new tests just mentioned, confirming the failure was self-caused and specific, not the platform flakiness it initially resembled.

None of these five fixes took the form of a broadened, general-purpose safeguard (for example, a rule requiring dependency-injection tests for every function, or a linter forbidding undocumented parameters). Each is scoped to the exact gap it closed.

## 5. Discussion

**What generalizes, and what does not.** The mechanism — verify a specific failure directly, then convert it into exactly one permanent, specific artifact — generalizes across all three case studies and across two independently developed codebases. The constraints themselves, by design, do not generalize past the failure that produced each one; Section 4.2 shows directly that attempting to abstract past that boundary would have produced a false rule.

**Resource implication.** Because each accumulated constraint is retained rather than rediscovered, the marginal human verification cost of a previously-seen failure mode trends toward zero as the castle grows, without requiring additional inference-time compute at execution time — no redundant unverified agents, no voting, no swarm. Cost concentrates once, at the point a failure is first verified, rather than being paid repeatedly by every future unverified attempt at the same class of task.

**Explicit limitation.** This paper reports case studies from two real projects, not a controlled experiment measuring an actual multi-agent, unverified baseline against the single-agent, constraint-accumulating condition described here on the same task. We make a mechanism claim, supported qualitatively by three independent instances, not a quantitative efficiency ratio. A controlled comparison — same task, same wall-clock or token budget, one run under an accumulated constraint set and one run as an unverified multi-agent baseline, with a real, pre-registered error metric — is the natural next step and is left to future work.

## 6. Conclusion

Across two independently developed open-source projects, we find the same pattern: a single agent operating under specific, accumulated, non-generalized constraints — each one the distilled result of one verified failure — catches the class of error that unverified agentic parallelism is typically proposed to address, and does so by retaining particular cases rather than by multiplying unverified attempts. The mechanism is supported by, and consistent with, established results in Case-Based Reasoning, regression testing practice, and the cost-asymmetry logic of cascaded model pipelines. We report this as a case-study finding, and explicitly do not claim a measured efficiency ratio against a real multi-agent baseline — that comparison remains future work.

## References

1. P. Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, arXiv:2005.11401 (2020).
2. V. Karpukhin et al., *Dense Passage Retrieval for Open-Domain Question Answering*, EMNLP 2020.
3. L. Mei et al., *A Survey of Context Engineering for Large Language Models*, arXiv:2507.13334 (2025).
4. Y. Wu et al., *ContextBudget: Budget-Aware Context Management for Long-Horizon Search Agents*, arXiv:2604.01664 (2026).
5. *Self-GC: Self-Governing Context for Long-Horizon LLM Agents*, arXiv:2607.00692 (2026).
6. *LLM Agents Are Latent Context Managers: Eliciting Self-Managed Context via a Proprioceptive Dashboard*, arXiv:2606.30005 (2026).
7. A. Aamodt, E. Plaza, *Case-Based Reasoning: Foundational Issues, Methodological Variations, and System Approaches*, AI Communications 7(1), 39–59 (1994).
8. A. Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, arXiv:2303.17651 (2023).
9. N. Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning*, arXiv:2303.11366, NeurIPS 2023.
10. L. Chen, M. Zaharia, J. Zou, *FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance*, arXiv:2305.05176 (2023).
11. J. P. Guilford, *The Structure of Intellect*, Psychological Bulletin, Technical Report 4 (1956).
12. Design Council (UK), *Eleven Lessons: A Study of the Design Process — The Double Diamond* (2005).
13. T. Baumgratz, M. Cramer, M. B. Plenio, *Quantifying Coherence*, Phys. Rev. Lett. 113, 140401 (2014). [background for Section 4.2's coherence-based signal, cited for completeness]
14. M. Polanyi, *The Tacit Dimension*, University of Chicago Press (1966).
15. B. W. Boehm, *Verifying and Validating Software Requirements and Design Specifications*, IEEE Software 1(1), 75–88 (1984).
