ALOF DATASET GENERATION RULES
=============================

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