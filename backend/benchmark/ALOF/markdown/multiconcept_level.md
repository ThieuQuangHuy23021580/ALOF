# ALOF BENCHMARK ADDON — MULTICONCEPT
> Dùng cùng PROMPT BASE. Addon này quy định benchmark multi-concept phức tạp.
## Mục tiêu benchmark
Đo diagnosis + strategy khi **current_task yêu cầu nhiều concept cùng lúc**, vocabulary đa dạng, có quan hệ prerequisite.
## Naming
- `case_id`: `adaptive_mc_001`, ...
- `learner_id`: `student_mc_001`, ...
## Quy mô (150 cases total)
| Tier | Cases | Concepts in current_task.concept_ids |
|------|-------|--------------------------------------|
| Easy | 50 | 2–3 |
| Medium | 50 | 4–6 |
| Hard | 50 | 7–10 |
## Vocabulary (toàn benchmark 150)
- Minimum: **50 unique** canonical concepts
- Recommended: **80–100 unique**
- Span ≥ **8 domains**: Mathematics, Physics, Chemistry, Biology, Computer Science, Languages, History, Geography, Economics, ...
- Mỗi tier: ≥ 6 domains, không dồn 1 domain
## Concept diversity (bắt buộc)
Mỗi tier phải có mix:
- concept count (theo tier)
- semantic diversity (khác domain/topic)
- concept relationships (related concepts trong cùng task)
- prerequisite relationships (vd: `common_denominator` trước `fraction_addition`)
- controlled reuse (concept lặp across cases, combo không lặp y hệt)
**Không** tạo concept giả chỉ để đủ số lượng.
**Không** thêm parent concept trừ khi câu hỏi thực sự cần.
## Task difficulty vs learner state
Task difficulty (Easy/Medium/Hard) = số concept + độ phức tạp task KHÔNG suy từ: diagnosis.level, mastery, accuracy, strategy.difficulty

Thiết kế history độc lập để tạo learner states đa dạng (weak/strong/partial).
## History design
- Length khuyến nghị: **4–12** interactions (ngắn hơn longcontext)
- Focus vào **concept overlap** với task, không cần distractor nhiều
- Memory gold: dùng **BASE default** (full overlap, history order)
## Multi-concept rules
### current_task.concept_ids
- Chỉ concept materially required
- Hard tier: 7–10 concepts từ ≥ 3 domains khi có thể
- Sắp xếp trong JSON không ảnh hư�ng gold; gold dùng alphabetical runtime
### weak_concepts
- Đánh giá **per concept**
- KHÔNG mark tất cả task concepts là weak
- Ví dụ: fraction_addition 2/2, common_denominator 1/2 → chỉ `common_denominator` weak
### diagnosis.concept
- = `primary_concepts[0]` (alphabetical first trong current_task.concept_ids)
- KHÔNG = concept yếu nhất (trừ khi trùng alphabetical)
### strategy focus_concepts
- Lấy từ nhánh decision tree, không auto-copy toàn bộ current_task.concept_ids
## Case archetypes (quota gợi ý / 50 cases)
| Archetype | ~Count | Pattern |
|-----------|--------|---------|
| Single weak in multi-task | 12 | 1 weak, rest OK |
| Multi weak | 8 | 2+ weak concepts |
| Transfer deficit | 8 | transfer branch → scaffold |
| All strong | 6 | challenge/deepening |
| Partial mastery | 8 | practice/targeted |
| Prerequisite chain | 8 | task có prerequisite concepts | 
## Validation riêng multiconcept
[ ] current_task concept count đúng tier [ ] ≥ 50 unique concepts (track running set khi sinh batch) [ ] không lặp combo concept_ids y hệt > 2 lần trong 50 cases [ ] weak evaluated per concept [ ] memory = full overlap list (BASE mode) [ ] mỗi tier ≥ 6 domains

## Lệnh thực thi
BENCHMARK: multiconcept TIER: [Easy | Medium | Hard] START: adaptive_mc_001 COUNT: 50 REGISTRY: [đính kèm] UNIQUE_CONCEPTS_TARGET: 80

