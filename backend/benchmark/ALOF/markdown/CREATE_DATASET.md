## LỆNH THỰC THI

PROMPT 0 — BASE (dùng chung cho mọi benchmark)
# ALOF BENCHMARK DATASET GENERATOR — BASE RULES
## Vai trò
Bạn tạo dataset JSONL cho ALOF. Mỗi case gồm `history`, `current_task`, `expected`.
Gold label PHẢI tính bằng thuật toán deterministic bên dưới — KHÔNG suy bằng trực giác.
## Quy tắc tuyệt đối
- KHÔNG bịa `concept_id` ngoài Concept Registry đính kèm
- KHÔNG copy expected từ ví dụ nếu chưa verify bằng thuật toán
- KHÔNG dùng enum ngoài danh sách cho phép
- Với mỗi case: thiết kế history + current_task TRƯỚC → tính expected → ghi JSON
- Output JSONL: 1 object / 1 dòng, JSON hợp lệ, không wrap trong `{"cases":[...]}`
---
## SCHEMA (bắt buộc)
```json
{
  "case_id": "adaptive_XXX",
  "learner": { "learner_id": "student_XXX" },
  "history": [{
    "interaction_id": "iXXX",
    "question_id": "qXXX",
    "question": "...",
    "answer": "...",
    "correct": true,
    "concept_ids": ["concept_a"],
    "timestamp": "2026-01-01T09:00:00Z"
  }],
  "current_task": {
    "question_id": "qtaskXXX",
    "question": "...",
    "concept_ids": ["concept_a"]
  },
  "expected": {
    "memory": { "relevant_interactions": ["qXXX"] },
    "diagnosis": {
      "concept": "concept_a",
      "level": "beginner",
      "weak_concepts": ["concept_a"]
    },
    "strategy": {
      "action": "explain",
      "strategy": "guided_explanation",
      "difficulty": "beginner",
      "focus_concepts": ["concept_a"]
    }
  }
}
---

## Natural Learning Trajectory

Generate realistic educational interactions, not synthetic concept combinations.

* **Question first, concepts second:** create a natural question and learner answer first, then assign `concept_ids` based only on concepts genuinely required by that question.
* Do NOT force concepts into a question just to satisfy benchmark requirements. Most interactions should involve only the concepts genuinely required by the question.
* If the active benchmark requires multiple concepts, difficulty should come from meaningful relationships across multiple interactions and the current task, not concept stuffing.
* Questions, answers, correct/incorrect labels, and learner progression must resemble a **real student learning trajectory**.
* Do NOT create incorrect answers, repeated failures, or concepts solely to force a desired `expected`.
* `current_task.concept_ids` must contain only concepts genuinely required by the task.
* Generate `expected` **after** the realistic history and current task are created, using the actual runtime as the source of truth.

Current Task: Create one coherent task appropriate to the active benchmark. Include only concepts genuinely needed to solve it; never add concepts just to increase the count.

## Field rules
history[]: bắt buộc đủ 7 field; timestamp ISO-8601 UTC (...Z)
current_task.concept_ids: chỉ concept materially required; không tự thêm parent
expected.memory.relevant_interactions: chỉ question_id, mọi id phải có trong history
question_id unique trong case (history + current_task)
ENUM (chỉ dùng các giá trị này)
Field	Values
diagnosis.level
beginner, intermediate, advanced
strategy.action
introduce, explain, scaffold, practice, review, challenge
strategy.strategy
direct_explanation, guided_explanation, step_by_step, targeted_practice, spaced_review, deepening
strategy.difficulty
beginner, medium, advanced
Cấm: unknown, mastered, easy, hard, guided,...
CONCEPT REGISTRY
Mọi concept_id phải có trong registry đính kèm
Format: English, lowercase_snake_case
Không tạo concept ad hoc, không dùng alias làm id
Multi-concept: chỉ tag concept thực sự cần cho câu hỏi
## MANDATORY CONCEPT LABEL VALIDATION

Before computing ANY expected field, validate every concept_id.

For each history interaction and current_task:

1. Read the question and answer independently from the assigned concept_ids.
2. Determine which canonical registry concept(s) are materially required.
3. Compare the result with the assigned concept_ids.
4. If any assigned concept is not genuinely required, REMOVE it.
5. If a genuinely required registry concept is missing, ADD it.
6. Never assign a concept merely to create relevant evidence,
   satisfy a quota, increase difficulty, or force an expected result.
7. Use the most specific canonical concept available in the registry.
8. Only after ALL concept_ids pass this validation may the generator
   compute expected.

Examples:
- Ohm's law → ohms_law
- molar mass → molar_mass
- cell membrane → cell_membrane
- fraction addition → fraction_addition
- passive voice → passive_voice
- opportunity cost → opportunity_cost
- inflation → inflation
- market equilibrium → market_equilibrium
- latitude/longitude → latitude_longitude
- contour-line interpretation → map_interpretation
## MANDATORY DETERMINISTIC REPLAY — NO GUESSING

Before writing `expected` for ANY case, the generator MUST explicitly
simulate the BASE/ADDON algorithm step by step.

For each case:

1. Replay ALL history interactions in chronological/history order.
2. Compute, for EVERY concept:
   - attempts
   - correct_attempts
   - accuracy
   - mastery
   - level
3. Compute Memory evidence exactly from the active benchmark rules.
4. Compute, for EVERY relevant concept:
   - relevant_evidence
   - recent_evidence
   - weakness_signal
   - transfer_deficit_signal
5. Compute:
   - primary_concepts
   - weak_concepts
   - transfer_deficit_concepts
6. Apply the Strategy Selector from TOP to BOTTOM.
7. Only then write `expected`.

IMPORTANT:
- Never infer a branch from the number of wrong answers alone.
- Never infer TRANSFER merely because relevant interactions are incorrect.
- TRANSFER requires ALL runtime conditions to be true.
- Never remove a concept from `weak_concepts` merely because it is new.
  If runtime weakness formula says mastery < 0.5, it is weak.
- INTRODUCE is a strategy branch and does NOT imply
  `weak_concepts` must be empty.
- A concept may simultaneously be `weak` and `transfer_deficit`;
  strategy must follow runtime branch priority.
- Do not stop calculation after identifying the first plausible branch.
- When a condition contains AND, verify EVERY operand separately.
- When a condition contains OR, verify at least one operand explicitly.
- Do not use semantic intuition to replace the runtime formula.

FINAL SELF-CHECK BEFORE OUTPUT:
For every case, verify:

`history → KnowledgeState → Memory → Evidence flags → Diagnosis → Strategy`

If any value was not deterministically calculated, do NOT output the case.

## DEFAULT GOLD GENERATION ALGORITHM
Các thuật toán dưới đây là DEFAULT của BASE.
Nếu active benchmark ADDON định nghĩa thuật toán tương ứng,
ADDON được ưu tiên và thay thế phần DEFAULT đó.
Bước 1 — Replay history (theo thứ tự history[])
Với mỗi interaction, với mỗi concept_id trong interaction.concept_ids:

attempts += 1
if correct: correct_attempts += 1
accuracy = correct_attempts / attempts
mastery = accuracy
level = infer_level(mastery)
infer_level:

mastery < 0.4  → beginner
mastery < 0.7  → intermediate
else           → advanced
Nếu attempts == 0: accuracy=0, mastery=0, level=beginner.

Lưu ý: Sau replay, mastery == accuracy (per concept).

Bước 2 — Memory
Chế độ mặc định của BASE:

TASK = current_task.concept_ids
RELEVANT = []
for H in history (theo thứ tự history[]):
  if H.concept_ids ∩ TASK ≠ ∅:
    append H.question_id to RELEVANT
Giữ đúng thứ tự duyệt history. Không lọc đúng/sai.

Chế độ longcontext: xem PROMPT ADDON longcontext (dùng ranked retrieval).

Bước 3 — Diagnosis
Constants: weakness_threshold=0.5, transfer_accuracy_threshold=0.5

Evidence flags (per concept C):

relevant_evidence(C):
  ∃ H in history: C ∈ H.concept_ids AND H.concept_ids ∩ TASK ≠ ∅
recent_evidence(C):
  C xuất hiện trong 5 interaction cuối (sort timestamp tăng dần, lấy 5 cuối)
  (history ≤ 5 → tất cả là recent)
Concept universe = concepts có state + TASK + concepts trong history.

Duyệt theo sorted(concept_id):

Weak:

weak(C) = mastery(C) < 0.5 OR (attempts(C) > 0 AND accuracy(C) < 0.5)
1/2 → accuracy 0.50 → KHÔNG weak vì accuracy
1/3 → 0.33 → weak
Transfer deficit:

transfer(C) = relevant_evidence(C) AND recent_evidence(C) AND accuracy(C) < 0.5
Primary concepts:

primary_concepts = [C for C in sorted(universe) if C in TASK]
Gold diagnosis:

expected.diagnosis.concept = primary_concepts[0]   // alphabetical first primary
expected.diagnosis.level = level(concept)
expected.diagnosis.weak_concepts = [C where weak(C)]  // alphabetical order
diagnosis.level = level của diagnosis.concept, không phải level trung bình.

Bước 4 — Strategy (decision tree, đúng runtime priority)

Áp dụng ĐÚNG thứ tự từ trên xuống dưới:

1. INTRODUCE

Có ít nhất một primary concept C thỏa ALL:

attempts(C) == 0
AND has_relevant_evidence(C) == false
AND has_recent_evidence(C) == false

→ action = introduce
→ strategy = direct_explanation
→ difficulty = beginner
→ focus_concepts = []

IMPORTANT:
- INTRODUCE được kiểm tra TRƯỚC transfer, weak, strong, partial.
- Không dùng `universe rỗng` làm điều kiện INTRODUCE.
- Concept mới vẫn có thể xuất hiện trong `weak_concepts` vì
  weak(C) được tính độc lập theo weakness formula.

2. TRANSFER

Nếu transfer_deficit_concepts != empty:

→ action = scaffold
→ strategy = step_by_step
→ difficulty = medium
→ focus_concepts = transfer concepts theo đúng runtime order

3. WEAK

Nếu weak_concepts != empty:

→ action = explain
→ strategy = guided_explanation
→ difficulty = beginner
→ focus_concepts = weak concepts theo đúng runtime order

4. STRONG

Nếu tồn tại C có mastery(C) >= 0.7:

→ action = challenge
→ strategy = deepening
→ difficulty = advanced
→ focus_concepts = strong concepts theo đúng runtime order

5. PARTIAL

Nếu tồn tại C có 0.4 <= mastery(C) < 0.7:

→ action = practice
→ strategy = targeted_practice
→ difficulty = medium
→ focus_concepts = partial concepts theo đúng runtime order

6. FALLBACK

→ action = review
→ strategy = spaced_review
→ difficulty = medium
→ focus_concepts = []

Strategy priority:
INTRODUCE > TRANSFER > WEAK > STRONG > PARTIAL > FALLBACK

`strategy.difficulty` độc lập với `diagnosis.level`.
Không suy strategy chỉ từ diagnosis.level.

CHECKLIST (mỗi case)
[ ] concept_id ∈ registry
[ ] expected tính từ thuật toán, không đoán
[ ] memory question_ids ∈ history
[ ] diagnosis.concept = primary_concepts[0]
[ ] diagnosis.level = level của diagnosis.concept
[ ] weak_concepts per-concept, đúng threshold
[ ] strategy khớp decision tree và đúng runtime priority
[ ] INTRODUCE được kiểm tra trước TRANSFER/WEAK/STRONG/PARTIAL
[ ] focus_concepts khớp đúng runtime output và runtime order
[ ] enum hợp lệ
[ ] JSONL 1 dòng / case
OUTPUT
Câu hỏi có thể tiếng Việt
concept_id luôn English snake_case
Sinh đủ số case theo lệnh thực thi + addon prompt

[ ] every history concept_id semantically validated against question
[ ] every current_task concept_id semantically validated against task
[ ] no concept_id exists only to create retrieval overlap
[ ] no concept_id is a broader/incorrect substitute when a specific
    registry concept exists



# PROMPT ADDON 1 — LONGCONTEXT

> Dùng cùng PROMPT BASE. Addon này override các rule liên quan đến LongContext.

## 1. Mục tiêu

Đo **Memory/Retrieval trên history dài**, tập trung vào:

* history length
* distractors
* temporal spread
* ranked Top-K retrieval

Không chủ động làm khó Diagnosis, Strategy hoặc Multiconcept reasoning.

## 2. Quy mô

| Tier   | Cases | History | Relevant ratio | Unique concepts | Task concepts |
| ------ | ----: | ------: | -------------: | --------------: | ------------: |
| Easy   |    50 |    5–10 |         40–60% |             2–4 |           1–2 |
| Medium |    50 |   11–20 |         20–40% |             4–8 |           1–2 |
| Hard   |    50 |   21–40 |         10–25% |           8–15+ |           1–2 |

Ưu tiên task 1 concept; chỉ dùng 2 concepts khi cả hai thực sự cần thiết.

`Relevant ratio = số history có concept overlap với current_task / tổng history`, cho phép ±5%.

## 3. History

* Easy: distractor chủ yếu khác domain.
* Medium: distractor cùng domain/topic nhưng khác concept.
* Hard: distractor cùng semantic neighborhood và có cạnh tranh retrieval.
* Distractor phải là câu hỏi học thuật tự nhiên.
* `concept_ids` chỉ chứa concepts thực sự cần thiết.

### Question Diversity — BẮT BUỘC

History là tập các learning events độc lập, không phải nhiều lần
hỏi lại cùng một bài.

Mỗi interaction phải đại diện cho một learning event có nội dung,
task và reasoning riêng.

Đối với mỗi interaction mới, xét TOÀN BỘ history đã tạo trước đó.

Mỗi interaction phải khác các interaction trước đó ở mức
semantic task, không chỉ ở mức câu chữ.

Một interaction mới chỉ được ACCEPT nếu ít nhất một trong các
thành phần sau thực sự thay đổi:

- task type;
- reasoning path;
- representation;
- context/application;
- information required to solve;
- output required from learner.

Chỉ thay đổi:

- wording;
- prefix/suffix;
- punctuation;
- numbers;
- names;
- variables;
- units;
- learner answer;
- correctness;
- timestamp

không tạo thành một learning event mới.

Hai interaction có cùng underlying task phải được xem là cùng một
learning event và không được xuất hiện cùng case.

Nếu không thể tạo variation hợp lệ cho concept đang chọn,
hãy chọn một concept khác trong allowed concept set thay vì
tạo lại cùng task structure.
### Task Structure Distribution — BẮT BUỘC

Không được để history tập trung quá mức vào một task structure.

Với mỗi concept xuất hiện nhiều lần:

- 1 occurrence → tự do.
- 2 occurrences → phải có task structure khác nhau.
- 3 occurrences → ít nhất 2 task structures.
- 4 occurrences → ít nhất 3 task structures.
- 5+ occurrences → ít nhất 3 task structures và không task
  structure nào chiếm quá 50% số occurrences của concept đó.

Các task structures được phân biệt ở mức semantic, ví dụ:

- direct computation;
- comparison;
- explanation;
- prediction;
- interpretation;
- application;
- error diagnosis;
- modeling;
- multi-step reasoning;
- concept identification.

Không tính variation nếu chỉ thay số liệu hoặc wording.

Nếu một concept không đủ task structures tự nhiên,
không tăng số occurrence của concept đó.
### Global Duplicate Check — BẮT BUỘC

Mỗi interaction mới phải được so sánh với TOÀN BỘ các interaction đã tạo trước đó trong cùng case.

Không chỉ kiểm tra exact string. Phải kiểm tra ở 3 mức:

1. Exact duplicate:
   cùng nội dung câu hỏi.

2. Near duplicate:
   chỉ thay wording, prefix/suffix, dấu câu, số liệu, tên người/vật/biến hoặc đơn vị.

3. Underlying-question duplicate:
   cùng concept + cùng task + cùng reasoning path + cùng answer target,
   dù cách diễn đạt khác nhau.

Nếu thuộc bất kỳ loại nào → REGENERATE interaction.

Không được chấp nhận nhiều interaction cùng một underlying question chỉ để tăng history length hoặc relevant ratio.

## 4. Temporal / Domain

* Easy: ~10 ngày.
* Medium: 20–40 ngày.
* Hard: 40–90+ ngày.
* Timestamp ISO-8601 UTC, tăng dần.
* Mỗi tier ≥6 domains.
* Không domain nào >30%.

## 5. Hard Retrieval

Mỗi Hard case:

* 4–5 relevant interactions;
* ≥2 relevant trước 50%;
* ≥1 relevant trong 25% đầu;
* không toàn bộ relevant ở 5 interactions cuối;
* có recent distractor;
* ≥2 điều kiện khó retrieval:

  * relevant ở xa;
  * relevant phân tán;
  * distractor cùng semantic neighborhood;
  * recent distractor;
  * ranking gần nhau;
  * không thể chỉ dùng recency.

Không đạt → **REGENERATE**.

## 6. MEMORY GOLD — Deterministic Top-K

```text
OVERLAP = history có concept overlap với TASK
RECENT = 5 interactions cuối
POOL = dedupe(OVERLAP + RECENT) theo question_id
```

```text
concept_overlap = |H.concept_ids ∩ TASK|
recency_score = (i + 1) / N
correctness_score = 2.0 nếu false, 1.0 nếu true, 0.0 otherwise
lexical_overlap = tính bằng implementation Python chính thức
```

```text
score =
    concept_overlap*8
    + recency_score*2
    + correctness_score
    + lexical_overlap*5
```

```text
TOP_K = 5
sort = (-score, -history_index)
```

Nếu `POOL < 5` → lấy toàn bộ.

Gold lưu tại:

```text
expected.memory.top_k_interactions
```

> `relevant` = concept overlap.
> `retrieved` = kết quả Top-K ranking.
> Hai khái niệm này không đồng nhất.

**Không chọn/chỉnh/reorder gold thủ công.**

## 7. Current Task

* 1–2 concepts, ưu tiên 1.
* Tất cả concepts phải thực sự cần thiết.
* Không copy/near-copy history.
* Không leak interaction cần retrieve.
* Không dùng `"Dựa trên lần trước..."`, question ID hoặc mô tả trực tiếp evidence target.

## 8. Diagnosis & Strategy

* Tính đúng **BASE algorithm**.
* Không cố tình tạo threshold/competing signals.
* Không cân bằng branch.
* Không dùng Diagnosis/Strategy để tạo LongContext difficulty.

## 9. Validation

* [ ] History đúng tier
* [ ] Relevant ratio ±5%
* [ ] Temporal span đúng
* [ ] Timestamp tăng dần
* [ ] Semantic mapping đúng
* [ ] Answer/correct đúng
* [ ] Không duplicate/near-duplicate
* [ ] Không cùng underlying question
* [ ] Không fake variation
* [ ] Current task không copy history
* [ ] Hard conditions đạt
* [ ] Memory = deterministic Top-K
* [ ] Diagnosis = BASE replay
* [ ] Strategy = BASE replay

## 10. Gold Pipeline

Generate case skeleton
→ Generate history sequentially
→ Acceptance Gate cho từng interaction
→ Global history diversity validation
→ Generate current task
→ Current-task independence validation
→ Structural validation
→ Semantic validation
→ Concept validation
→ Temporal/Domain validation
→ Difficulty validation
→ Python Memory Top-K
→ Python KnowledgeState
→ Python BASE Diagnosis
→ Python BASE Strategy
→ Final validation
→ ACCEPT
### Sequential Generation Rule

History phải được tạo tuần tự.

Không generate toàn bộ history rồi mới cố gắng sửa duplicate.

Mỗi interaction phải vượt qua Acceptance Gate trước khi
được thêm vào history.

Generator phải duy trì trạng thái của:

- concepts đã sử dụng;
- task structures đã sử dụng;
- contexts đã sử dụng;
- reasoning paths đã sử dụng.

Các trạng thái này được dùng để quyết định interaction tiếp theo.

> **LLM tạo dữ liệu; Python/runtime tạo ground truth.**
> Vi phạm rule bắt buộc → **REGENERATE**, không sửa `expected` thủ công.

## CONCEPT REGISTRY
{
  "registry_name": "ALOF Benchmark Concept Registry",
  "registry_version": "1.0",
  "purpose": "Controlled canonical vocabulary for ALOF benchmark dataset generation.",
  "canonical_naming_rules": {
    "language": "English",
    "format": "lowercase_snake_case",
    "stable_id": true,
    "question_specific_ids_allowed": false,
    "learner_state_ids_allowed": false,
    "strategy_or_difficulty_ids_allowed": false
  },
  "concept_count": 100,
  "domains": [
    "biology",
    "chemistry",
    "computer_science",
    "economics",
    "geography",
    "history",
    "languages",
    "mathematics",
    "physics"
  ],
  "concepts": [
    {
      "concept_id": "fraction_addition",
      "canonical_name": "fraction_addition",
      "domain": "mathematics",
      "topic": "fractions",
      "description": "Adding two or more fractions.",
      "status": "active"
    },
    {
      "concept_id": "fraction_subtraction",
      "canonical_name": "fraction_subtraction",
      "domain": "mathematics",
      "topic": "fractions",
      "description": "Subtracting one fraction from another.",
      "status": "active"
    },
    {
      "concept_id": "fraction_multiplication",
      "canonical_name": "fraction_multiplication",
      "domain": "mathematics",
      "topic": "fractions",
      "description": "Multiplying fractions.",
      "status": "active"
    },
    {
      "concept_id": "fraction_division",
      "canonical_name": "fraction_division",
      "domain": "mathematics",
      "topic": "fractions",
      "description": "Dividing fractions.",
      "status": "active"
    },
    {
      "concept_id": "common_denominator",
      "canonical_name": "common_denominator",
      "domain": "mathematics",
      "topic": "fractions",
      "description": "Finding a common denominator for fractions.",
      "status": "active"
    },
    {
      "concept_id": "fraction_comparison",
      "canonical_name": "fraction_comparison",
      "domain": "mathematics",
      "topic": "fractions",
      "description": "Comparing the values of fractions.",
      "status": "active"
    },
    {
      "concept_id": "equivalent_fractions",
      "canonical_name": "equivalent_fractions",
      "domain": "mathematics",
      "topic": "fractions",
      "description": "Identifying and generating equivalent fractions.",
      "status": "active"
    },
    {
      "concept_id": "percentage",
      "canonical_name": "percentage",
      "domain": "mathematics",
      "topic": "arithmetic",
      "description": "Understanding and calculating percentages.",
      "status": "active"
    },
    {
      "concept_id": "ratio",
      "canonical_name": "ratio",
      "domain": "mathematics",
      "topic": "arithmetic",
      "description": "Comparing quantities using ratios.",
      "status": "active"
    },
    {
      "concept_id": "proportion",
      "canonical_name": "proportion",
      "domain": "mathematics",
      "topic": "arithmetic",
      "description": "Solving relationships involving proportional quantities.",
      "status": "active"
    },
    {
      "concept_id": "linear_equation",
      "canonical_name": "linear_equation",
      "domain": "mathematics",
      "topic": "algebra",
      "description": "Solving equations of first degree.",
      "status": "active"
    },
    {
      "concept_id": "linear_inequality",
      "canonical_name": "linear_inequality",
      "domain": "mathematics",
      "topic": "algebra",
      "description": "Solving inequalities involving linear expressions.",
      "status": "active"
    },
    {
      "concept_id": "quadratic_equation",
      "canonical_name": "quadratic_equation",
      "domain": "mathematics",
      "topic": "algebra",
      "description": "Solving equations of second degree.",
      "status": "active"
    },
    {
      "concept_id": "quadratic_formula",
      "canonical_name": "quadratic_formula",
      "domain": "mathematics",
      "topic": "algebra",
      "description": "Using the quadratic formula to solve quadratic equations.",
      "status": "active"
    },
    {
      "concept_id": "polynomial_operations",
      "canonical_name": "polynomial_operations",
      "domain": "mathematics",
      "topic": "algebra",
      "description": "Adding, subtracting, and multiplying polynomials.",
      "status": "active"
    },
    {
      "concept_id": "exponentiation",
      "canonical_name": "exponentiation",
      "domain": "mathematics",
      "topic": "arithmetic",
      "description": "Working with powers and exponents.",
      "status": "active"
    },
    {
      "concept_id": "square_root",
      "canonical_name": "square_root",
      "domain": "mathematics",
      "topic": "arithmetic",
      "description": "Understanding and calculating square roots.",
      "status": "active"
    },
    {
      "concept_id": "probability",
      "canonical_name": "probability",
      "domain": "mathematics",
      "topic": "statistics_and_probability",
      "description": "Calculating the likelihood of events.",
      "status": "active"
    },
    {
      "concept_id": "mean_median_mode",
      "canonical_name": "mean_median_mode",
      "domain": "mathematics",
      "topic": "statistics_and_probability",
      "description": "Calculating and interpreting common measures of central tendency.",
      "status": "active"
    },
    {
      "concept_id": "rectangle_area",
      "canonical_name": "rectangle_area",
      "domain": "mathematics",
      "topic": "geometry",
      "description": "Calculating the area of rectangles.",
      "status": "active"
    },
    {
      "concept_id": "distance_displacement",
      "canonical_name": "distance_displacement",
      "domain": "physics",
      "topic": "kinematics",
      "description": "Distinguishing distance from displacement.",
      "status": "active"
    },
    {
      "concept_id": "speed",
      "canonical_name": "speed",
      "domain": "physics",
      "topic": "kinematics",
      "description": "Calculating and interpreting speed.",
      "status": "active"
    },
    {
      "concept_id": "velocity",
      "canonical_name": "velocity",
      "domain": "physics",
      "topic": "kinematics",
      "description": "Calculating and interpreting velocity.",
      "status": "active"
    },
    {
      "concept_id": "acceleration",
      "canonical_name": "acceleration",
      "domain": "physics",
      "topic": "kinematics",
      "description": "Understanding changes in velocity over time.",
      "status": "active"
    },
    {
      "concept_id": "motion_graphs",
      "canonical_name": "motion_graphs",
      "domain": "physics",
      "topic": "kinematics",
      "description": "Interpreting position, velocity, and motion graphs.",
      "status": "active"
    },
    {
      "concept_id": "force",
      "canonical_name": "force",
      "domain": "physics",
      "topic": "mechanics",
      "description": "Understanding force as an interaction that changes motion.",
      "status": "active"
    },
    {
      "concept_id": "newtons_first_law",
      "canonical_name": "newtons_first_law",
      "domain": "physics",
      "topic": "mechanics",
      "description": "Applying Newton's first law of motion.",
      "status": "active"
    },
    {
      "concept_id": "newtons_second_law",
      "canonical_name": "newtons_second_law",
      "domain": "physics",
      "topic": "mechanics",
      "description": "Relating force, mass, and acceleration.",
      "status": "active"
    },
    {
      "concept_id": "newtons_third_law",
      "canonical_name": "newtons_third_law",
      "domain": "physics",
      "topic": "mechanics",
      "description": "Applying Newton's third law of motion.",
      "status": "active"
    },
    {
      "concept_id": "work",
      "canonical_name": "work",
      "domain": "physics",
      "topic": "mechanics",
      "description": "Understanding mechanical work.",
      "status": "active"
    },
    {
      "concept_id": "kinetic_energy",
      "canonical_name": "kinetic_energy",
      "domain": "physics",
      "topic": "energy",
      "description": "Understanding energy associated with motion.",
      "status": "active"
    },
    {
      "concept_id": "potential_energy",
      "canonical_name": "potential_energy",
      "domain": "physics",
      "topic": "energy",
      "description": "Understanding stored potential energy.",
      "status": "active"
    },
    {
      "concept_id": "momentum",
      "canonical_name": "momentum",
      "domain": "physics",
      "topic": "mechanics",
      "description": "Understanding linear momentum.",
      "status": "active"
    },
    {
      "concept_id": "electric_current",
      "canonical_name": "electric_current",
      "domain": "physics",
      "topic": "electricity",
      "description": "Understanding electric current in circuits.",
      "status": "active"
    },
    {
      "concept_id": "ohms_law",
      "canonical_name": "ohms_law",
      "domain": "physics",
      "topic": "electricity",
      "description": "Relating voltage, current, and resistance.",
      "status": "active"
    },
    {
      "concept_id": "atomic_structure",
      "canonical_name": "atomic_structure",
      "domain": "chemistry",
      "topic": "general_chemistry",
      "description": "Understanding the structure of atoms.",
      "status": "active"
    },
    {
      "concept_id": "periodic_table",
      "canonical_name": "periodic_table",
      "domain": "chemistry",
      "topic": "general_chemistry",
      "description": "Interpreting organization and trends in the periodic table.",
      "status": "active"
    },
    {
      "concept_id": "chemical_bond",
      "canonical_name": "chemical_bond",
      "domain": "chemistry",
      "topic": "chemical_bonding",
      "description": "Understanding chemical bonding between atoms.",
      "status": "active"
    },
    {
      "concept_id": "ionic_bond",
      "canonical_name": "ionic_bond",
      "domain": "chemistry",
      "topic": "chemical_bonding",
      "description": "Understanding ionic bonding.",
      "status": "active"
    },
    {
      "concept_id": "covalent_bond",
      "canonical_name": "covalent_bond",
      "domain": "chemistry",
      "topic": "chemical_bonding",
      "description": "Understanding covalent bonding.",
      "status": "active"
    },
    {
      "concept_id": "chemical_formula",
      "canonical_name": "chemical_formula",
      "domain": "chemistry",
      "topic": "chemical_language",
      "description": "Interpreting and constructing chemical formulas.",
      "status": "active"
    },
    {
      "concept_id": "chemical_equation",
      "canonical_name": "chemical_equation",
      "domain": "chemistry",
      "topic": "chemical_reactions",
      "description": "Representing chemical reactions with equations.",
      "status": "active"
    },
    {
      "concept_id": "reaction_balancing",
      "canonical_name": "reaction_balancing",
      "domain": "chemistry",
      "topic": "chemical_reactions",
      "description": "Balancing chemical equations.",
      "status": "active"
    },
    {
      "concept_id": "mole_concept",
      "canonical_name": "mole_concept",
      "domain": "chemistry",
      "topic": "quantitative_chemistry",
      "description": "Understanding the mole as a counting unit.",
      "status": "active"
    },
    {
      "concept_id": "molar_mass",
      "canonical_name": "molar_mass",
      "domain": "chemistry",
      "topic": "quantitative_chemistry",
      "description": "Calculating molar mass.",
      "status": "active"
    },
    {
      "concept_id": "stoichiometry",
      "canonical_name": "stoichiometry",
      "domain": "chemistry",
      "topic": "quantitative_chemistry",
      "description": "Calculating quantitative relationships in chemical reactions.",
      "status": "active"
    },
    {
      "concept_id": "acid_base",
      "canonical_name": "acid_base",
      "domain": "chemistry",
      "topic": "solutions_and_acids",
      "description": "Understanding acids and bases.",
      "status": "active"
    },
    {
      "concept_id": "ph_scale",
      "canonical_name": "ph_scale",
      "domain": "chemistry",
      "topic": "solutions_and_acids",
      "description": "Interpreting pH and acidity/basicity.",
      "status": "active"
    },
    {
      "concept_id": "chemical_equilibrium",
      "canonical_name": "chemical_equilibrium",
      "domain": "chemistry",
      "topic": "chemical_reactions",
      "description": "Understanding dynamic equilibrium in reversible reactions.",
      "status": "active"
    },
    {
      "concept_id": "oxidation_reduction",
      "canonical_name": "oxidation_reduction",
      "domain": "chemistry",
      "topic": "chemical_reactions",
      "description": "Understanding oxidation and reduction processes.",
      "status": "active"
    },
    {
      "concept_id": "cell_structure",
      "canonical_name": "cell_structure",
      "domain": "biology",
      "topic": "cell_biology",
      "description": "Understanding the structures and functions of cells.",
      "status": "active"
    },
    {
      "concept_id": "cell_membrane",
      "canonical_name": "cell_membrane",
      "domain": "biology",
      "topic": "cell_biology",
      "description": "Understanding the structure and transport role of cell membranes.",
      "status": "active"
    },
    {
      "concept_id": "cellular_transport",
      "canonical_name": "cellular_transport",
      "domain": "biology",
      "topic": "cell_biology",
      "description": "Understanding movement of substances across cell membranes.",
      "status": "active"
    },
    {
      "concept_id": "mitosis",
      "canonical_name": "mitosis",
      "domain": "biology",
      "topic": "cell_division",
      "description": "Understanding mitotic cell division.",
      "status": "active"
    },
    {
      "concept_id": "meiosis",
      "canonical_name": "meiosis",
      "domain": "biology",
      "topic": "cell_division",
      "description": "Understanding meiotic cell division.",
      "status": "active"
    },
    {
      "concept_id": "dna_structure",
      "canonical_name": "dna_structure",
      "domain": "biology",
      "topic": "genetics",
      "description": "Understanding DNA structure.",
      "status": "active"
    },
    {
      "concept_id": "dna_replication",
      "canonical_name": "dna_replication",
      "domain": "biology",
      "topic": "genetics",
      "description": "Understanding how DNA is replicated.",
      "status": "active"
    },
    {
      "concept_id": "gene_expression",
      "canonical_name": "gene_expression",
      "domain": "biology",
      "topic": "genetics",
      "description": "Understanding how genetic information is expressed.",
      "status": "active"
    },
    {
      "concept_id": "genetics",
      "canonical_name": "genetics",
      "domain": "biology",
      "topic": "genetics",
      "description": "Understanding inheritance and genetic variation.",
      "status": "active"
    },
    {
      "concept_id": "natural_selection",
      "canonical_name": "natural_selection",
      "domain": "biology",
      "topic": "evolution",
      "description": "Understanding natural selection as a mechanism of evolution.",
      "status": "active"
    },
    {
      "concept_id": "photosynthesis",
      "canonical_name": "photosynthesis",
      "domain": "biology",
      "topic": "plant_biology",
      "description": "Understanding conversion of light energy into chemical energy in plants.",
      "status": "active"
    },
    {
      "concept_id": "cellular_respiration",
      "canonical_name": "cellular_respiration",
      "domain": "biology",
      "topic": "cellular_metabolism",
      "description": "Understanding cellular energy production.",
      "status": "active"
    },
    {
      "concept_id": "ecosystem",
      "canonical_name": "ecosystem",
      "domain": "biology",
      "topic": "ecology",
      "description": "Understanding interactions among organisms and their environment.",
      "status": "active"
    },
    {
      "concept_id": "food_chain",
      "canonical_name": "food_chain",
      "domain": "biology",
      "topic": "ecology",
      "description": "Understanding transfer of energy through feeding relationships.",
      "status": "active"
    },
    {
      "concept_id": "homeostasis",
      "canonical_name": "homeostasis",
      "domain": "biology",
      "topic": "physiology",
      "description": "Understanding regulation of stable internal conditions.",
      "status": "active"
    },
    {
      "concept_id": "variable",
      "canonical_name": "variable",
      "domain": "computer_science",
      "topic": "programming",
      "description": "Understanding variables and stored values in programs.",
      "status": "active"
    },
    {
      "concept_id": "data_type",
      "canonical_name": "data_type",
      "domain": "computer_science",
      "topic": "programming",
      "description": "Understanding types of data handled by programs.",
      "status": "active"
    },
    {
      "concept_id": "conditional_statement",
      "canonical_name": "conditional_statement",
      "domain": "computer_science",
      "topic": "programming",
      "description": "Using conditions to control program execution.",
      "status": "active"
    },
    {
      "concept_id": "loop",
      "canonical_name": "loop",
      "domain": "computer_science",
      "topic": "programming",
      "description": "Using repetition constructs in programs.",
      "status": "active"
    },
    {
      "concept_id": "function",
      "canonical_name": "function",
      "domain": "computer_science",
      "topic": "programming",
      "description": "Defining and using reusable functions.",
      "status": "active"
    },
    {
      "concept_id": "recursion",
      "canonical_name": "recursion",
      "domain": "computer_science",
      "topic": "programming",
      "description": "Solving problems through recursive function calls.",
      "status": "active"
    },
    {
      "concept_id": "algorithm",
      "canonical_name": "algorithm",
      "domain": "computer_science",
      "topic": "algorithms",
      "description": "Understanding step-by-step computational procedures.",
      "status": "active"
    },
    {
      "concept_id": "algorithm_complexity",
      "canonical_name": "algorithm_complexity",
      "domain": "computer_science",
      "topic": "algorithms",
      "description": "Analyzing computational complexity of algorithms.",
      "status": "active"
    },
    {
      "concept_id": "array",
      "canonical_name": "array",
      "domain": "computer_science",
      "topic": "data_structures",
      "description": "Understanding indexed collections of values.",
      "status": "active"
    },
    {
      "concept_id": "linked_list",
      "canonical_name": "linked_list",
      "domain": "computer_science",
      "topic": "data_structures",
      "description": "Understanding linked-list data structures.",
      "status": "active"
    },
    {
      "concept_id": "stack",
      "canonical_name": "stack",
      "domain": "computer_science",
      "topic": "data_structures",
      "description": "Understanding last-in-first-out stack structures.",
      "status": "active"
    },
    {
      "concept_id": "queue",
      "canonical_name": "queue",
      "domain": "computer_science",
      "topic": "data_structures",
      "description": "Understanding first-in-first-out queue structures.",
      "status": "active"
    },
    {
      "concept_id": "tree",
      "canonical_name": "tree",
      "domain": "computer_science",
      "topic": "data_structures",
      "description": "Understanding hierarchical tree data structures.",
      "status": "active"
    },
    {
      "concept_id": "database",
      "canonical_name": "database",
      "domain": "computer_science",
      "topic": "data_management",
      "description": "Understanding structured storage and retrieval of data.",
      "status": "active"
    },
    {
      "concept_id": "sql_query",
      "canonical_name": "sql_query",
      "domain": "computer_science",
      "topic": "databases",
      "description": "Writing and understanding SQL queries.",
      "status": "active"
    },
    {
      "concept_id": "subject_verb_agreement",
      "canonical_name": "subject_verb_agreement",
      "domain": "languages",
      "topic": "english_grammar",
      "description": "Matching subjects and verbs correctly.",
      "status": "active"
    },
    {
      "concept_id": "verb_tense",
      "canonical_name": "verb_tense",
      "domain": "languages",
      "topic": "english_grammar",
      "description": "Using and distinguishing English verb tenses.",
      "status": "active"
    },
    {
      "concept_id": "modal_verbs",
      "canonical_name": "modal_verbs",
      "domain": "languages",
      "topic": "english_grammar",
      "description": "Using modal verbs to express ability, possibility, obligation, and related meanings.",
      "status": "active"
    },
    {
      "concept_id": "passive_voice",
      "canonical_name": "passive_voice",
      "domain": "languages",
      "topic": "english_grammar",
      "description": "Understanding and forming passive constructions.",
      "status": "active"
    },
    {
      "concept_id": "conditional_sentence",
      "canonical_name": "conditional_sentence",
      "domain": "languages",
      "topic": "english_grammar",
      "description": "Understanding and using conditional sentences.",
      "status": "active"
    },
    {
      "concept_id": "reading_comprehension",
      "canonical_name": "reading_comprehension",
      "domain": "languages",
      "topic": "english_reading",
      "description": "Extracting and interpreting meaning from written passages.",
      "status": "active"
    },
    {
      "concept_id": "vocabulary_in_context",
      "canonical_name": "vocabulary_in_context",
      "domain": "languages",
      "topic": "english_vocabulary",
      "description": "Inferring word meaning from contextual clues.",
      "status": "active"
    },
    {
      "concept_id": "paragraph_structure",
      "canonical_name": "paragraph_structure",
      "domain": "languages",
      "topic": "writing",
      "description": "Organizing ideas into coherent paragraphs.",
      "status": "active"
    },
    {
      "concept_id": "historical_chronology",
      "canonical_name": "historical_chronology",
      "domain": "history",
      "topic": "historical_thinking",
      "description": "Ordering and relating events in historical time.",
      "status": "active"
    },
    {
      "concept_id": "cause_and_effect",
      "canonical_name": "cause_and_effect",
      "domain": "history",
      "topic": "historical_thinking",
      "description": "Analyzing causal relationships among historical events.",
      "status": "active"
    },
    {
      "concept_id": "historical_evidence",
      "canonical_name": "historical_evidence",
      "domain": "history",
      "topic": "historical_thinking",
      "description": "Evaluating evidence used to understand historical events.",
      "status": "active"
    },
    {
      "concept_id": "historical_perspective",
      "canonical_name": "historical_perspective",
      "domain": "history",
      "topic": "historical_thinking",
      "description": "Interpreting events from different historical perspectives.",
      "status": "active"
    },
    {
      "concept_id": "map_interpretation",
      "canonical_name": "map_interpretation",
      "domain": "geography",
      "topic": "geographic_skills",
      "description": "Reading and interpreting maps.",
      "status": "active"
    },
    {
      "concept_id": "latitude_longitude",
      "canonical_name": "latitude_longitude",
      "domain": "geography",
      "topic": "geographic_skills",
      "description": "Using latitude and longitude to locate places.",
      "status": "active"
    },
    {
      "concept_id": "climate_patterns",
      "canonical_name": "climate_patterns",
      "domain": "geography",
      "topic": "physical_geography",
      "description": "Understanding geographic patterns of climate.",
      "status": "active"
    },
    {
      "concept_id": "population_distribution",
      "canonical_name": "population_distribution",
      "domain": "geography",
      "topic": "human_geography",
      "description": "Understanding how populations are distributed geographically.",
      "status": "active"
    },
    {
      "concept_id": "supply_demand",
      "canonical_name": "supply_demand",
      "domain": "economics",
      "topic": "microeconomics",
      "description": "Understanding interactions between supply and demand.",
      "status": "active"
    },
    {
      "concept_id": "opportunity_cost",
      "canonical_name": "opportunity_cost",
      "domain": "economics",
      "topic": "economic_reasoning",
      "description": "Understanding the value of the next-best alternative forgone.",
      "status": "active"
    },
    {
      "concept_id": "inflation",
      "canonical_name": "inflation",
      "domain": "economics",
      "topic": "macroeconomics",
      "description": "Understanding sustained increases in the general price level.",
      "status": "active"
    },
    {
      "concept_id": "market_equilibrium",
      "canonical_name": "market_equilibrium",
      "domain": "economics",
      "topic": "microeconomics",
      "description": "Understanding equilibrium between market supply and demand.",
      "status": "active"
    }
  ]
}

---

Sinh dataset theo lệnh:
- BENCHMARK: longcontext
- TIER: medium
- START: adaptive_lc_051
- COUNT: 50

Output: file JSONL thuần, không markdown wrapper, không giải thích dài.
Mỗi case đã verify checklist.

