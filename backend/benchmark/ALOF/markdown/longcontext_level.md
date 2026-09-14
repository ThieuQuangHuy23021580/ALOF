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

