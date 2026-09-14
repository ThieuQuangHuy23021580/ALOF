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
GOLD GENERATION ALGORITHM (BẮT BUỘC)
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
Chế độ mặc định (multiconcept / strategy / base):

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

Bước 4 — Strategy (decision tree, ưu tiên trên → dưới)
#	Condition	action	strategy	difficulty	focus_concepts
1
universe rỗng
introduce
direct_explanation
beginner
[]
2
transfer_deficit non-empty
scaffold
step_by_step
medium
transfer concepts (alphabetical)
3
weak_concepts non-empty
explain
guided_explanation
beginner
weak_concepts (alphabetical)
4
∃ C: mastery(C) ≥ 0.7
challenge
deepening
advanced
strong concepts (sorted universe order)
5
∃ C: 0.4 ≤ mastery(C) < 0.7
practice
targeted_practice
medium
partial concepts (sorted order)
6
fallback
review
spaced_review
medium
[]
strategy.difficulty độc lập diagnosis.level
Không suy strategy chỉ từ level
CHECKLIST (mỗi case)
[ ] concept_id ∈ registry
[ ] expected tính từ thuật toán, không đoán
[ ] memory question_ids ∈ history
[ ] diagnosis.concept = primary_concepts[0]
[ ] diagnosis.level = level của diagnosis.concept
[ ] weak_concepts per-concept, đúng threshold
[ ] strategy khớp decision tree
[ ] focus_concepts khớp nhánh strategy
[ ] enum hợp lệ
[ ] JSONL 1 dòng / case
OUTPUT
Câu hỏi có thể tiếng Việt
concept_id luôn English snake_case
Sinh đủ số case theo lệnh thực thi + addon prompt

