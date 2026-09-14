ALOF DATASET GENERATION RULES
=============================

MULTICONCEPT BENCHMARK DIFFICULTY

For a 150-case Multiconcept benchmark:

    Easy:
        50 cases
        2–3 concepts per current task

    Medium:
        50 cases
        4–6 concepts per current task

    Hard:
        50 cases
        7–10 concepts per current task

The benchmark MUST use a diverse canonical vocabulary.

Minimum:
    50 unique canonical concepts

Recommended:
    80–100 unique canonical concepts

Concepts SHOULD span at least 8 learning domains,
including but not limited to:

    Mathematics
    Physics
    Chemistry
    Biology
    Computer Science
    Languages
    History
    Geography
    Economics

Difficulty MUST reflect concept complexity, not learner knowledge.

Difficulty MUST NOT be inferred from:

    diagnosis.level
    mastery
    accuracy
    strategy.difficulty

Each difficulty level MUST contain multiple domains.

Concept diversity MUST include:

    concept count
    semantic diversity
    concept relationships
    prerequisite relationships
    controlled concept reuse

Do NOT create artificial concepts solely to satisfy
the required concept count.

All concepts MUST come from the canonical ALOF
Concept Registry.

current_task.concept_ids MUST contain only concepts
materially required by the task.

Parent concepts MUST NOT be added automatically
unless they are explicitly required by runtime semantics.

The dataset MUST NOT become a collection of repeated
combinations of a small number of concepts.

1. HISTORY
- Every interaction must contain:
    interaction_id
    question_id
    question
    answer
    correct
    concept_ids
    timestamp

- timestamp must be ISO-8601.
- concept_ids must use canonical concept IDs.
- question_id must uniquely identify the interaction/question within the dataset.

2. CURRENT TASK
- current_task.question_id is unique.
- current_task.concept_ids are the concepts required by the task.
- Do NOT assume current_task.concept_ids[0] is the primary diagnosis concept.

3. MEMORY
- memory.relevant_interactions contains question_id only.
- Every question_id must come from history.
- Select interactions relevant to current_task.
- Prefer concept overlap with current_task.concept_ids.
- Recent interactions may be preferred when supported by runtime behavior.
- Preserve the exact ordering returned by the memory runtime.
- Do NOT include answer, correct, concept_ids, timestamp, or other fields in expected memory.

Schema:
    "memory": {
        "relevant_interactions": ["q123", "q456"]
    }

4. DIAGNOSIS CONCEPT
- diagnosis.concept is the primary concept selected by the runtime.
- It may differ from current_task.concept_ids[0].
- For multi-concept tasks, determine the concept from the actual
  diagnosis/runtime logic and available evidence.
- Never mechanically assign:
      diagnosis.concept = current_task.concept_ids[0]
- Gold data must reproduce the exact runtime-selected concept.

Example:

    current_task.concept_ids = [
        "fraction_addition",
        "common_denominator"
    ]

Runtime may return:

    diagnosis.concept = "common_denominator"

Gold must use:

    "common_denominator"

5. KNOWLEDGE LEVEL
Only three KnowledgeLevel values are valid:

    beginner
    intermediate
    advanced

KnowledgeState level is derived from mastery:

    mastery < 0.4
        -> beginner

    0.4 <= mastery < 0.7
        -> intermediate

    mastery >= 0.7
        -> advanced

Do NOT use:

    unknown
    mastered

IMPORTANT:
- level is determined from the runtime KnowledgeState.
- Do NOT derive level directly from the number of correct answers.
- Do NOT assume:
      mastery = accuracy
- mastery and accuracy are independent signals.
- When generating benchmark data, replay history using the actual
  ALOF state-update logic before determining the expected level.

6. ACCURACY
Accuracy is:

    accuracy = correct_attempts / attempts

Examples:

    0/2 -> 0.00
    1/2 -> 0.50
    2/3 -> 0.67
    3/3 -> 1.00

If attempts == 0:

    accuracy = 0.0

7. WEAK CONCEPT
According to the current KnowledgeStateDiagnoser:

    weak_concept =
        mastery < 0.5
        OR
        accuracy < 0.5

Therefore:

    3/3 correct
        accuracy = 1.00
        -> not weak by accuracy

    2/3 correct
        accuracy = 0.67
        -> not weak by accuracy

    1/2 correct
        accuracy = 0.50
        -> not weak by accuracy alone

    1/3 correct
        accuracy = 0.33
        -> weak

    0/2 correct
        accuracy = 0.00
        -> weak

IMPORTANT:
- mastery must come from the actual KnowledgeState.
- Do NOT replace mastery with accuracy.
- A concept can be weak because of low mastery even when accuracy >= 0.5.

Do NOT mark a concept weak merely because:
- it is in current_task;
- it is the primary concept;
- it appeared recently;
- it is the first concept in concept_ids;
- another concept was answered incorrectly.

8. MULTI-CONCEPT WEAK RULE
Weakness must be evaluated per concept.

Example:

    fraction_addition:
        2/2 correct

    common_denominator:
        1/2 correct

Expected:

    weak_concepts = [
        "common_denominator"
    ]

Do NOT mark all current-task concepts as weak.

9. WEAK_CONCEPT ORDER
- Preserve the ordering produced by the runtime.
- Do NOT alphabetically sort weak_concepts.
- Do NOT reorder weak_concepts according to current_task.concept_ids
  unless that is exactly what the runtime does.

10. STRATEGY
Strategy must represent the actual runtime Strategy Selector decision.

Canonical TeachingActionType:

    introduce
    explain
    scaffold
    practice
    review
    challenge

Canonical TeachingStrategy:

    direct_explanation
    guided_explanation
    step_by_step
    targeted_practice
    spaced_review
    deepening

Canonical difficulty:

    beginner
    medium
    advanced

IMPORTANT:
Do NOT generate strategy solely from diagnosis.level.

The following are knowledge-level decision patterns:

    weak knowledge
        -> commonly explain / guided_explanation / beginner

    strong mastery
        -> commonly challenge / deepening / advanced

    partial mastery
        -> commonly practice / targeted_practice / medium

BUT these are NOT sufficient as a universal gold-generation formula.

The actual runtime may select:

    scaffold
    step_by_step
    review
    or other valid combinations

based on additional diagnosis/context signals.

Therefore:

    expected.strategy = actual runtime strategy

not:

    expected.strategy = human intuition

11. DIAGNOSIS LEVEL VS STRATEGY DIFFICULTY
These fields are independent.

Example:

    diagnosis.level = "advanced"
    strategy.difficulty = "medium"

is VALID if produced by the runtime.

Never force:

    diagnosis.level == strategy.difficulty

12. FOCUS CONCEPTS
- focus_concepts must represent the concepts selected by the runtime
  for the teaching action.
- Do NOT automatically copy current_task.concept_ids.
- Do NOT automatically copy diagnosis.concept.
- Preserve runtime ordering.

13. EXPECTED OUTPUT
Every benchmark record must contain:

    expected.memory
    expected.diagnosis
    expected.strategy

Do NOT add evaluator-specific aliases.

Gold data must describe runtime semantics, not human intuition.

14. GOLD DATA GENERATION PRINCIPLE
The runtime is the source of truth.

For each new benchmark case:

    history
        ↓
    KnowledgeState update
        ↓
    Memory runtime
        ↓
    Diagnosis runtime
        ↓
    Strategy runtime
        ↓
    expected

Do NOT manually infer expected values when the corresponding
runtime behavior can be executed and observed.

If runtime returns:

    concept = common_denominator

Gold must contain:

    concept = common_denominator

even if a human might consider:

    fraction_addition

the more obvious concept.

15. ENUM SAFETY
Only use canonical enum values.

KnowledgeLevel:
    beginner
    intermediate
    advanced

TeachingActionType:
    introduce
    explain
    scaffold
    practice
    review
    challenge

TeachingStrategy:
    direct_explanation
    guided_explanation
    step_by_step
    targeted_practice
    spaced_review
    deepening

difficulty:
    beginner
    medium
    advanced

Never introduce:

    unknown
    mastered
    intermediate_level
    hard
    easy
    guided
    step-by-step

16. EXACT-MATCH SAFETY
When the evaluator compares a field exactly:

- preserve runtime values;
- preserve runtime list ordering;
- preserve canonical enum spelling;
- do not add extra fields;
- do not remove required fields;
- do not normalize values inside the evaluator to compensate for bad gold data.

17. FINAL VALIDATION
Before adding a new dataset case, verify:

    [ ] all question_ids come from history where required
    [ ] current_task concept_ids are canonical
    [ ] diagnosis.concept matches runtime
    [ ] mastery was obtained from actual KnowledgeState logic
    [ ] level matches mastery threshold
    [ ] weak_concepts matches mastery/accuracy logic
    [ ] weak_concepts are evaluated per concept
    [ ] strategy matches actual Strategy Selector/runtime
    [ ] strategy.difficulty is not inferred from diagnosis.level
    [ ] focus_concepts matches runtime
    [ ] list ordering matches runtime
    [ ] all enum values are canonical
    [ ] no evaluator-specific aliases were added

18. DATASET SCHEMA
==================

Each dataset record MUST follow exactly this structure:

{
  "case_id": "adaptive_XXX",

  "learner": {
    "learner_id": "student_XXX"
  },

  "history": [
    {
      "interaction_id": "iXXX",
      "question_id": "qXXX",
      "question": "...",
      "answer": "...",
      "correct": true,
      "concept_ids": [
        "concept_a"
      ],
      "timestamp": "2026-01-01T09:00:00Z"
    }
  ],

  "current_task": {
    "question_id": "qXXX",
    "question": "...",
    "concept_ids": [
      "concept_a"
    ]
  },

  "expected": {
    "memory": {
      "relevant_interactions": [
        "qXXX"
      ]
    },

    "diagnosis": {
      "concept": "concept_a",
      "level": "beginner",
      "weak_concepts": [
        "concept_a"
      ]
    },

    "strategy": {
      "action": "scaffold",
      "strategy": "step_by_step",
      "difficulty": "medium",
      "focus_concepts": [
        "concept_a"
      ]
    }
  }
}

FIELD REQUIREMENTS
------------------

Top-level fields:
    case_id
    learner
    history
    current_task
    expected

learner:
    learner_id

history[]:
    interaction_id
    question_id
    question
    answer
    correct
    concept_ids
    timestamp

current_task:
    question_id
    question
    concept_ids

expected:
    memory
    diagnosis
    strategy

expected.memory:
    relevant_interactions

expected.diagnosis:
    concept
    level
    weak_concepts

expected.strategy:
    action
    strategy
    difficulty
    focus_concepts


FIELD TYPES
-----------

case_id:
    string

learner.learner_id:
    string

history:
    array of objects

history[].interaction_id:
    string

history[].question_id:
    string

history[].question:
    string

history[].answer:
    string

history[].correct:
    boolean

history[].concept_ids:
    array[string]

history[].timestamp:
    string
    ISO-8601 format

current_task.question_id:
    string

current_task.question:
    string

current_task.concept_ids:
    array[string]

expected.memory.relevant_interactions:
    array[string]

expected.diagnosis.concept:
    string

expected.diagnosis.level:
    enum:
        beginner
        intermediate
        advanced

expected.diagnosis.weak_concepts:
    array[string]

expected.strategy.action:
    enum:
        introduce
        explain
        scaffold
        practice
        review
        challenge

expected.strategy.strategy:
    enum:
        direct_explanation
        guided_explanation
        step_by_step
        targeted_practice
        spaced_review
        deepening

expected.strategy.difficulty:
    enum:
        beginner
        medium
        advanced

expected.strategy.focus_concepts:
    array[string]


JSONL FORMAT
------------

The dataset is JSONL.

One JSON object = one line.

Example:

{"case_id":"adaptive_001", ...}
{"case_id":"adaptive_002", ...}
{"case_id":"adaptive_003", ...}

Do NOT wrap the dataset in:

{
  "cases": [...]
}

Each line must be independently valid JSON.

Real-example:
{"case_id":"adaptive_lc_001","learner":{"learner_id":"student_lc_001"},"history":[{"interaction_id":"i001","question_id":"q001","question":"Tính 25% của 80.","answer":"20","correct":true,"concept_ids":["percentage"],"timestamp":"2026-01-01T09:00:00Z"},{"interaction_id":"i002","question_id":"q002","question":"Tính diện tích hình chữ nhật dài 8 cm, rộng 5 cm.","answer":"40 cm²","correct":true,"concept_ids":["rectangle_area"],"timestamp":"2026-01-02T09:00:00Z"},{"interaction_id":"i003","question_id":"q003","question":"Tính 1/4 + 1/4.","answer":"1/2","correct":true,"concept_ids":["fraction_addition"],"timestamp":"2026-01-03T09:00:00Z"},{"interaction_id":"i004","question_id":"q004","question":"Giải x + 7 = 12.","answer":"x = 5","correct":true,"concept_ids":["linear_equation"],"timestamp":"2026-01-04T09:00:00Z"},{"interaction_id":"i005","question_id":"q005","question":"Quy đồng 1/3 và 1/6.","answer":"2/6 và 1/6","correct":false,"concept_ids":["common_denominator"],"timestamp":"2026-01-05T09:00:00Z"},{"interaction_id":"i006","question_id":"q006","question":"Tính chu vi hình chữ nhật dài 7 cm, rộng 4 cm.","answer":"22 cm","correct":true,"concept_ids":["rectangle_perimeter"],"timestamp":"2026-01-06T09:00:00Z"},{"interaction_id":"i007","question_id":"q007","question":"Tính 3 × (-4).","answer":"-12","correct":true,"concept_ids":["integer_multiplication","negative_integers"],"timestamp":"2026-01-07T09:00:00Z"},{"interaction_id":"i008","question_id":"q008","question":"So sánh 3/4 và 2/3.","answer":"3/4 > 2/3","correct":true,"concept_ids":["fraction_comparison"],"timestamp":"2026-01-08T09:00:00Z"},{"interaction_id":"i009","question_id":"q009","question":"Quy đồng 2/5 và 3/10.","answer":"4/10 và 3/10","correct":false,"concept_ids":["common_denominator"],"timestamp":"2026-01-09T09:00:00Z"},{"interaction_id":"i010","question_id":"q010","question":"Tính 15% của 200.","answer":"30","correct":true,"concept_ids":["percentage"],"timestamp":"2026-01-10T09:00:00Z"}],"current_task":{"question_id":"qmc001","question":"Tính 2/3 + 1/4 bằng cách quy đồng mẫu số trước khi cộng.","concept_ids":["fraction_addition","common_denominator"]},"expected":{"memory":{"relevant_interactions":["q005","q009","q003"]},"diagnosis":{"concept":"common_denominator","level":"beginner","weak_concepts":["common_denominator"]},"strategy":{"action":"scaffold","strategy":"step_by_step","difficulty":"medium","focus_concepts":["common_denominator","fraction_addition"]}}}


19. CANONICAL CONCEPT VOCABULARY
================================

1. CANONICAL CONCEPT ID
- Every concept_id MUST refer to a concept registered in the
  ALOF Concept Registry.
- A concept_id MUST NOT be created ad hoc during dataset generation.
- concept_ids MUST be stable identifiers, independent of wording,
  language, question text, learner state, or dataset case.

2. CANONICAL NAME
Every registered concept MUST have:

    concept_id
    canonical_name
    description

canonical_name MUST:
    - use English;
    - use lowercase snake_case;
    - represent a reusable educational concept;
    - use established educational terminology;
    - be language-independent;
    - be specific enough to distinguish the concept;
    - be general enough to apply to multiple questions.

Do NOT use:
    - question text;
    - learner-specific descriptions;
    - examples;
    - numbers;
    - timestamps;
    - case IDs;
    - dataset-specific names;
    - version suffixes.

Valid:

    fraction_addition
    common_denominator
    quadratic_equation
    rectangle_area

Invalid:

    add_2_fractions
    fraction_addition_question_001
    student_weak_fraction
    adding_fractions_v2
    calculate_2_3_plus_1_4

3. EXISTING-CONCEPT-FIRST
- Before proposing a new concept, the system MUST search the existing
  Concept Registry.
- If an existing concept has the same semantic meaning, reuse it.
- Do NOT create a new concept merely because:
    - the wording differs;
    - the language differs;
    - the question format differs;
    - a synonym is used;
    - the educational context differs.

Example:

    "fraction_addition"
    "adding_fractions"
    "fraction_sum"

MUST NOT become three canonical concepts if they represent
the same learning concept.

4. ALIAS CONTROL
- Alternative names MUST be stored as aliases of the canonical concept.
- Aliases MUST NOT become canonical concept_ids.

Example:

    canonical_name:
        fraction_addition

    aliases:
        cộng phân số
        adding fractions
        fraction sum

All MUST resolve to:

    fraction_addition

5. HIERARCHY CONSTRAINT
- Every concept MUST belong to an appropriate position in the
  Concept Hierarchy.
- Prefer an existing parent concept.
- A new parent may be created only when no suitable parent exists.
- Do NOT create a new hierarchy branch for every question.

Recommended hierarchy:

    domain
      ↓
    topic
      ↓
    concept
      ↓
    sub-concept (only when necessary)

6. SEMANTIC DUPLICATE CHECK
- Before registering a new concept, compare it against existing concepts
  using semantic similarity and/or ontology matching.
- If the candidate is semantically equivalent to an existing concept,
  reuse the existing concept.
- If similarity is ambiguous, mark the candidate as pending review.
- Do NOT automatically create a canonical concept from a low-confidence
  proposal.

7. CONCEPT GRANULARITY
- Concepts MUST represent reusable learning knowledge or skills.
- Do NOT create concepts that are merely:
    - individual questions;
    - question templates;
    - answer patterns;
    - learner states;
    - errors;
    - difficulty levels;
    - teaching strategies.

For example:

    common_denominator

is a concept.

These are NOT concepts:

    student_weakness
    easy_fraction_question
    incorrect_answer
    step_by_step_strategy

8. MULTI-CONCEPT RULE
- A question MAY contain multiple concept_ids.
- Include only concepts that are materially required by the question.
- Do NOT add related concepts merely because they are semantically close.
- Do NOT automatically include parent concepts unless the runtime
  explicitly represents them as required concepts.

Example:

    current_task.concept_ids = [
        "fraction_addition",
        "common_denominator"
    ]

Do NOT automatically add:

    fractions
    arithmetic
    mathematics

unless those are explicitly represented as required concepts
by the ALOF concept extraction/runtime.

9. CONCEPT RELATION ≠ CONCEPT ID
Semantic relationships MUST NOT be encoded by inventing additional
concept IDs.

Use relations such as:

    prerequisite
    related
    similar
    part_of

Example:

    fraction_addition
        prerequisite → common_denominator

Do NOT create:

    fraction_addition_requires_common_denominator

10. CROSS-LANGUAGE NORMALIZATION
- Different languages MUST resolve to the same canonical concept.
- Canonical concept IDs MUST NOT depend on the language of the question.

Example:

    "cộng phân số"
    "adding fractions"
    "addition de fractions"

MUST resolve to the same canonical concept:

    fraction_addition

11. DATASET VOCABULARY BOUNDARY
- Benchmark datasets MUST use only concepts registered in the
  canonical Concept Registry.
- Dataset generation MUST NOT silently introduce new concept names.
- If a required concept does not exist:
      → propose concept
      → validate concept
      → register concept
      → then generate dataset case.

12. VOCABULARY VALIDATION
Before accepting a dataset case:

    [ ] every concept_id exists in Concept Registry
    [ ] every concept_id is canonical
    [ ] no alias is used as concept_id
    [ ] no duplicate semantic concepts are present
    [ ] concept hierarchy is valid
    [ ] concept granularity is valid
    [ ] multi-concept assignment contains only required concepts
    [ ] canonical IDs are language-independent
    [ ] no question-specific concept was created