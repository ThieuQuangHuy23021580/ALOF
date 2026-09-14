
BENCHMARK ADDON: STRATEGY

GOAL
Evaluate:
Learner Performance → Diagnosis → Adaptive Teaching Strategy

Do NOT evaluate:
User wording → strategy.

RUNTIME IS SOURCE OF TRUTH
Runtime diagnosis/selector is authoritative.
Do not invent or override:
- mastery
- accuracy
- weak_concepts
- transfer_deficit_concepts
- branch priority
- focus_concepts/order
- action
- strategy
- difficulty

If dataset gold conflicts with runtime, regenerate the case.
If runtime behavior is unclear, STOP and report.

==================================================
1. DATASET
==================================================

TOTAL = 150 cases

DIFFICULTY:
- Easy = 50
- Medium = 50
- Hard = 50

BRANCH:
- B1 INTRODUCE = 5
- B2 TRANSFER = 35
- B3 WEAK = 35
- B4 STRONG = 35
- B5 PARTIAL = 40
- B6 REVIEW/FALLBACK = 0

Every case must contain real academic learning content.

BAN:
- generic study skills
- time management
- planning
- note taking
- motivation
- self-assessment
- study habits
- meta-learning

Use concepts from the attached Concept Registry only.

==================================================
2. LEARNING TRAJECTORY
==================================================

Generate:

academic question
→ learner answer
→ correct/incorrect
→ concept evidence
→ learning trajectory
→ KnowledgeState
→ Memory
→ Diagnosis
→ Strategy

Do NOT generate a desired strategy first and fabricate history to match it.

History:
- about 8 interactions ±1
- timestamps roughly 8–14 days
- realistic academic questions/answers
- 30–50% distractors
- preferably 1 concept/interaction
- 2 concepts only when naturally required
- avoid excessive exact repetition

Current task:
- coherent academic task
- only genuinely required concepts
- normally 1 concept
- 2 concepts only when directly related
- never add concepts only to increase count

==================================================
3. FIVE STRATEGY BRANCHES
==================================================

B1 — INTRODUCE

Target concept is genuinely new:

attempts(C) == 0
AND has_relevant_evidence(C) == false
AND has_recent_evidence(C) == false

IMPORTANT:
B1 INTRODUCE determines the STRATEGY branch only.
It does not determine `diagnosis.weak_concepts`.

A new concept with mastery = 0 satisfies:
weak(C) = true
under the BASE weakness formula.

Therefore a valid INTRODUCE case may have:
strategy.action = introduce
AND
diagnosis.weak_concepts = [the new concept].

Runtime priority.

Expected:
action = introduce
strategy = direct_explanation
difficulty = beginner
focus_concepts = []

Do not use concept_ids=[] as the normal way to create INTRODUCE.
Use an actual new academic concept.

--------------------------------------------------

B2 — TRANSFER DEFICIT

Conditions:
- transfer_deficit_concepts != empty
- transfer has priority over weak
- relevant + recent evidence exists
- accuracy < 0.5 according to runtime

Expected:
action = scaffold
strategy = step_by_step
difficulty = medium
focus_concepts = runtime-selected transfer concepts

--------------------------------------------------

B3 — WEAK

Conditions:
- transfer_deficit_concepts == empty
- weak_concepts != empty

Typical runtime signal:
mastery < 0.5
OR
attempts > 0 AND accuracy < 0.5

Expected:
action = explain
strategy = guided_explanation
difficulty = beginner
focus_concepts = runtime-selected weak concepts

--------------------------------------------------

B4 — STRONG

Conditions:
- no transfer deficit
- no weakness
- at least one concept with mastery >= 0.7

Expected:
action = challenge
strategy = deepening
difficulty = advanced
focus_concepts = runtime-selected strong concepts

--------------------------------------------------

B5 — PARTIAL

Conditions:
- no transfer deficit
- no weakness
- no strong concept
- mastery in [0.4, 0.7)

```

Expected:
action = practice
strategy = targeted_practice
difficulty = medium
focus_concepts = runtime-selected partial concepts

--------------------------------------------------

NO B6
Do NOT generate REVIEW or FALLBACK cases.

==================================================
4. THRESHOLD CASES
==================================================

Include boundary cases where supported by runtime:

accuracy:
0.49 / 0.50 / 0.51

mastery:
0.39 / 0.40 / 0.69 / 0.70

transfer:
0.49 / 0.50

Do not assume formulas. Verify against actual runtime.

==================================================
5. DIFFICULTY
==================================================

Benchmark Difficulty ≠ Diagnosis Level ≠ Strategy Difficulty.

Easy:
- clear signal
- simple trajectory
- usually 1 primary concept

Medium:
- moderately complex trajectory
- mixed evidence
- near-boundary cases

Hard:
- complex/ambiguous trajectory
- competing signals
- multiple related concepts
- transfer/weakness interactions
- threshold cases
- focus ordering matters

Hard means benchmark complexity,
NOT necessarily a difficult academic question.

==================================================
5A. HARD CASE QUALITY GATE — MANDATORY
==================================================

A case labeled HARD is valid ONLY if it contains at least ONE
genuine benchmark-complexity mechanism.

The academic question itself does NOT make a case Hard.

A HARD case MUST contain at least one of:

1. THRESHOLD BOUNDARY
   - accuracy = 0.49 / 0.50 / 0.51
   - mastery = 0.39 / 0.40 / 0.69 / 0.70
   - transfer condition near 0.5

2. COMPETING SIGNALS
   - at least one concept is simultaneously:
     weak = true
     AND
     transfer_deficit = true
   - therefore the generator must verify that TRANSFER wins
     because of runtime priority.

3. MULTI-CONCEPT DECISION
   - current_task requires 2 or more genuinely related concepts
   - the concepts have different KnowledgeState signals
   - the resulting strategy depends on evaluating multiple concepts.

4. FOCUS-ORDER CHALLENGE
   - 2 or more concepts qualify for the selected strategy branch
   - the generator must determine their order from the actual runtime
   - alphabetical ordering MUST NOT be assumed unless runtime does so.

5. EVIDENCE-BOUNDARY CHALLENGE
   - relevant_evidence and recent_evidence differ across concepts
   - this difference affects transfer/weakness classification.

--------------------------------------------------
HARD INVALIDATION RULE
--------------------------------------------------

The following patterns are NOT sufficient to qualify as HARD:

- simple 6/8 correct → mastery 0.75 → STRONG
- simple 7/8 correct → mastery 0.875 → STRONG
- simple 2/5 correct → mastery 0.40 → TRANSFER
- simple 3/8 correct → mastery 0.375 → WEAK

A case that produces a valid runtime branch but does not contain
a genuine Hard mechanism is still INVALID as a HARD benchmark case.

If a generated HARD case does not satisfy at least one mechanism
above:

→ DO NOT OUTPUT THE CASE.
→ REGENERATE history/current_task.
→ Recompute the entire deterministic replay.
→ Recheck the Hard Quality Gate.

The generator MUST NOT modify expected labels merely to make a case
appear Hard.

--------------------------------------------------
HARD CASE INTERNAL VALIDATION
--------------------------------------------------

Before accepting every HARD case, verify:

[ ] At least one Hard mechanism is genuinely present.
[ ] The mechanism arises naturally from the learning trajectory.
[ ] No concept was added only to create difficulty.
[ ] Expected values are still produced entirely by runtime rules.
[ ] The selected strategy branch is correct.
[ ] The case would distinguish a robust implementation from a
    naive majority-count or simple-rule implementation.

If any item fails → REGENERATE.
==================================================
6. DOMAIN COVERAGE
==================================================

Use at least 8 domains overall.

Each of B2–B5:
- at least 4 domains

Each benchmark difficulty:
- at least 6 domains

Do not make the dataset Mathematics-only.

==================================================
7. FOCUS CONCEPTS
==================================================

focus_concepts MUST come from runtime.

Preserve runtime order.

Do NOT alphabetically sort unless runtime itself does so.

==================================================
8. GOLD GENERATION
==================================================

For every case:

1. Generate history.
2. Generate current task.
3. Replay history into KnowledgeState.
4. Build Memory evidence.
5. Run Diagnosis.
6. Run Strategy Selector.
7. Identify runtime branch.
8. Copy runtime action/strategy/difficulty/focus.
9. Validate schema + vocabulary.
10. Validate branch quota.

Never manually override runtime output.

==================================================
9. FINAL VALIDATION
==================================================

Required:

Easy = 50
Medium = 50
Hard = 50

B1 = 5
B2 = 35
B3 = 35
B4 = 35
B5 = 40
B6 = 0

All concepts ∈ Concept Registry.

No generic study-skills cases.

No REVIEW/FALLBACK.

No unnecessary concepts.

No invented runtime behavior.

Output JSONL only.

---
