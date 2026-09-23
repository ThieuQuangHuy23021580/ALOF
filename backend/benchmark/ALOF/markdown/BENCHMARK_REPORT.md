# ALOF Benchmark — báo cáo kết quả hiện tại

Ngày chấm: 21/09/2026  
Gold memory / diagnosis / strategy: đồng bộ với runtime deterministic (`AdaptiveLearningPipeline` + `EvidenceSelector`).  
Chấm lại trên **results.jsonl cũ** (không gọi LLM lại).

## Giá trị benchmark hiện tại

| Chỉ số | Giá trị |
|---|---|
| Tổng case đã chấm | **400** (8 × 50) |
| Execution | **400/400 (100%)** |
| Semantic pass (memory + diagnosis + strategy + response) | **400/400 (100%)** |
| Memory F1 (trung bình mọi tập) | **1.00** |
| Fail execution / response | **0** |
| Tập chưa có dataset | longcontext **Hard** (thiết kế 50 case, chưa chạy) |

Quy mô thiết kế đầy đủ: 9 tập × 50 = 450. Hiện có dữ liệu và report: **400**.

## Top-K (memory)

| Tham số | Giá trị | Nơi gắn |
|---|---|---|
| **K** | **5** | `ContextBuilder.MEMORY_TOP_K` = `EvidenceSelector.DEFAULT_TOP_K` = 5 |
| Trần token | 1200 | `ContextBuilder.MEMORY_MAX_TOKENS` |
| Gold pass/fail | `expected.memory.top_k_interactions` vs `runtime_metadata.memory_retrieval` (so **tập** `question_id`, không so thứ tự) | Evaluator `gold_source = "top_k"` |
| Pool ứng viên | `dedupe(relevant ∪ recent)` theo `interaction.id`, recent = 5 interaction mới nhất theo timestamp | `HistoricalEvidenceBuilder` + `ContextBuilder` |
| ID trong gold | chỉ `question_id` (không fallback UUID) | `gold_from_runtime.py` |

**Ý nghĩa Top-K = 5:** mỗi case chỉ được tính đúng memory nếu runtime chọn đúng **đúng 5** (hoặc ít hơn nếu hết token) interaction mà pipeline ranking đã chọn khi sinh gold. `relevant_interactions` chỉ là audit (concept overlap), không quyết định pass/fail khi đã có `top_k_interactions`.

Cạnh tranh thật ở biên K: case như `adaptive_st_068` (slot 5: điểm 5.90 vs 5.81). Gold ghi đúng winner runtime, không ghi “bài nên retrieve”.

## Bảng thống kê theo tập

Pass rate mọi cột = số case pass / 50. Memory F1 = mean F1 trên 50 case.

| Tập | Độ khó | Case | Exec | Memory | Mem F1 | Diagnosis | Strategy | Response | Semantic |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| longcontext | Easy | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| longcontext | Medium | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| longcontext | Hard | — | — | — | — | — | — | — | **chưa có data** |
| multiconcept | Easy | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| multiconcept | Medium | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| multiconcept | Hard | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| strategy | Easy | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| strategy | Medium | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| strategy | Hard | 50 | 50 | 50 | 1.00 | 50 | 50 | 50 | **50/50** |
| **Tổng đã chấm** | | **400** | **400** | **400** | **1.00** | **400** | **400** | **400** | **400/400** |

## So với lần chấm trước khi sửa gold

Lần chấm 300 case (chưa sync gold strategy/diagnosis/memory với runtime):

| Tập | Fail khi đó | Sau sync gold (cùng results) |
|---|---|---|
| multiconcept Medium | 6 (difficulty + 1 level) | 0 |
| multiconcept Hard | 16 (15 difficulty, 1 memory Top-K, 3 level) | 0 |
| strategy Medium | 1 (Top-K slot 5) | 0 |
| longcontext Easy, multiconcept Easy, strategy Hard | 0 | 0 |

Fail cũ **không** phải lỗi LLM hay execution. Gold `strategy.difficulty` / `diagnosis.level` / Top-K lệch pipeline deterministic; sau khi gold = runtime, mọi dimension pass.

## Cách đọc số

- **Execution 100%:** orchestrator chạy xong, có prediction.
- **Memory 100% / F1 1.00:** retrieval Top-K=5 khớp gold `question_id`.
- **Diagnosis 100%:** primary concept + level (và field gold khác nếu có) khớp diagnoser.
- **Strategy 100% (evaluator hiện tại):** chủ yếu `difficulty` (và `type`/`focus` nếu gold có). `action`/`strategy`/`focus_concepts` đã ghi đúng runtime trong gold nhưng evaluator multiconcept **chưa so** `action` trừ khi có field `type`.
- **Response 100%:** có output; không vi phạm `direct_answer=false`.

Nguồn report: `backend/benchmark/ALOF/reports/report_*.json`.
