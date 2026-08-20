# ALOF DEVELOPMENT CONTEXT — CONTINUATION PROMPT

Tôi đang phát triển dự án **ALOF (Adaptive Learning Orchestration Framework)** — một hệ thống Adaptive Learning Multi-Agent.

## Mục tiêu hiện tại

Không tiếp tục ưu tiên benchmark/SILO-BENCH. Benchmark đã được triển khai đủ để phục vụ đánh giá kiến trúc và hiện tại **tạm dừng test benchmark để tập trung hoàn thiện ALOF**.

Mục tiêu là xây dựng một phiên bản ALOF đầu tiên:

- chạy được end-to-end;
- có kiến trúc Multi-Agent rõ ràng;
- có khả năng adaptive learning cơ bản;
- có Routing → Planning → Workflow → Runtime → Component;
- có Learning State / Student / Knowledge / Goal làm nền tảng;
- có thể mở rộng sau này;
- đủ khác biệt với một chatbot thông thường;
- KHÔNG over-engineering;
- ưu tiên hoàn thành MVP nhanh, rõ kiến trúc và dễ demo/bảo vệ.

## Kiến trúc hiện tại

Luồng chính:

User Request
    ↓
LearningOrchestrator
    ↓
Router
    ├── IntentRecognizer
    └── ComponentSelector
    ↓
Planner
    ↓
WorkflowBuilder
    ↓
Runtime / Scheduler
    ↓
ComponentExecutor
    ↓
Learning Components
    ├── Mentor
    ├── Research
    ├── Planner
    ├── Quiz
    └── Flashcard
    ↓
RuntimeResult
    ↓
Application / API / Flutter

Các tầng chính:

- `domain/`
  - student
  - learning
  - knowledge
  - goal
  - workflow
  - artifact

- `core/`
  - component
  - registry
  - executor
  - context
  - result
  - lifecycle
  - parser

- `application/`
  - routing
  - planning
  - orchestration
  - runtime
  - services

- `components/`
  - mentor
  - research
  - planner
  - benchmark (không ưu tiên phát triển tiếp)

- `infrastructure/`
  - prompts
  - providers

- `benchmark/`
  - giữ nguyên, không phát triển thêm trừ khi tôi yêu cầu.

## Những phần đã có

### Routing

Đã có:

- `IntentRecognizer`
- `IntentResult`
- `IntentItem`
- `LLMIntentRecognizer`
- `Router`
- `LLMRouter`
- `RoutingResult`
- `ComponentSelector`

Intent hiện tại:

- explain
- summarize
- compare
- roadmap
- quiz
- flashcard
- unknown

Mapping hiện tại:

- explain → mentor
- summarize → mentor
- compare → research → mentor
- roadmap → planner
- quiz → quiz
- flashcard → flashcard

### Planning

Đã có:

- `Planner`
- `PlanningRequest`
- `Plan`
- `PlanStep`
- `LLMSequentialPlanner`
- `SequentialPlanner`
- `WorkflowBuilder`
- `SequentialWorkflowBuilder`

LLM planner hiện tạo logical execution plan từ RoutingResult.

### Orchestration

Đã có:

`LearningOrchestrator.execute()`:

1. Router
2. Planning
3. Workflow Building
4. Runtime Execution

### Runtime

Đã có:

- Runtime
- RuntimeContext
- RuntimeResult
- SequentialRuntime
- Scheduler
- SequentialScheduler
- ComponentExecution

### Component system

Đã có:

- Component
- ComponentRegistry
- ComponentExecutor
- DefaultComponentExecutor
- ComponentContext
- ComponentContextBuilder
- ComponentResult
- DependencyContext
- lifecycle/status
- JSON parser

### Components

Đã có:

- MentorComponent
- ResearchComponent
- PlannerComponent

Benchmark components tồn tại riêng và không được coi là learning components chính.

### Domain

Đã có:

- Student
- Profile
- LearningPreference
- LearningProgress
- LearningState
- KnowledgeNode
- KnowledgeLevel
- LearningGoal
- GoalStatus
- Workflow
- WorkflowNode
- WorkflowEdge
- Task
- Artifact

## Phong cách làm việc

Tôi muốn phát triển theo kiểu:

1. Mỗi lần chỉ làm **một milestone rõ ràng**.
2. Ưu tiên implementation đơn giản nhưng đúng kiến trúc.
3. Không over-engineering.
4. Không tự ý quay lại benchmark.
5. Không tạo abstraction chỉ để "đẹp kiến trúc".
6. Nếu cần code hiện tại để chỉnh sửa chính xác → yêu cầu tôi gửi file.
7. Khi tôi gửi file → trả lại **TOÀN BỘ FILE CODE HOÀN CHỈNH**, không chỉ đoạn diff.
8. Code phải đồng bộ với kiến trúc hiện tại và tránh tạo lỗi import/type/interface.
9. Sau mỗi milestone:
   - ghi rõ đã hoàn thành gì;
   - cập nhật cây kiến trúc/quá trình;
   - chỉ ra milestone tiếp theo.
10. Không đưa roadmap dài lại mỗi lần. Chỉ tập trung milestone hiện tại.

## MVP TARGET

ALOF MVP cần chứng minh được rằng đây KHÔNG chỉ là chatbot.

Một request như:

"Giải thích REST và GraphQL, sau đó cho tôi biết nên dùng cái nào."

phải có thể đi theo hướng:

User
→ Intent Recognition
→ Multi-intent Routing
→ Planning
→ Workflow

Research
→ tạo knowledge/artifact trung gian

Mentor
→ nhận artifact từ Research
→ giải thích/adapt cho learner

→ RuntimeResult

Điểm quan trọng:

**Các component phải phối hợp với nhau thông qua workflow/context/artifact, thay vì chỉ gọi nhiều LLM rồi ghép text.**

## MVP Adaptive Learning

Sau orchestration cơ bản, ưu tiên hoàn thiện:

1. LearningState được đưa vào Runtime/ComponentContext.
2. Component có thể đọc learner state.
3. Component có thể tạo learning artifact.
4. Artifact từ component trước có thể trở thành input của component sau.
5. Runtime cập nhật learning state sau execution.
6. Planner có thể sử dụng learner state để tạo plan.

Sau đó:

7. QuizComponent.
8. Quiz result → update LearningState.
9. Planner/Mentor thay đổi hành vi dựa trên LearningState.

Đây là phần tạo khác biệt chính của ALOF so với chatbot.

## ROADMAP NGẮN NHẤT

### MILESTONE 1 — Hoàn thiện Execution Context / Artifact Flow
Mục tiêu:
Component A → Artifact → Component B.

Cần kiểm tra/chỉnh:
- RuntimeContext
- ComponentContext
- ComponentResult
- Artifact
- WorkflowNode
- SequentialRuntime

Đảm bảo output của component trước truyền được sang component sau một cách rõ ràng.

### MILESTONE 2 — Hoàn thiện Learning State trong Runtime
Mục tiêu:
Runtime thực sự biết learner đang ở trạng thái nào.

Cần:
- đưa LearningState vào RuntimeContext;
- ComponentContext đọc được LearningState;
- Component có thể tạo learning-state update;
- Runtime áp dụng update.

### MILESTONE 3 — Hoàn thiện Adaptive Mentor
Mentor không chỉ trả lời câu hỏi.

Mentor phải sử dụng:
- learner profile;
- learning preference;
- knowledge level;
- learning progress/state;
- artifact từ component trước.

Ví dụ:
beginner → giải thích nền tảng;
advanced → giải thích ngắn, đi sâu;
weak knowledge node → tăng giải thích/ôn tập.

### MILESTONE 4 — Quiz Component
Thêm:

`components/quiz/quiz_component.py`

Flow:

Mentor/Planner
→ Quiz
→ QuizResult
→ LearningState Update

Quiz không chỉ là chatbot tạo câu hỏi; kết quả phải ảnh hưởng learner state.

### MILESTONE 5 — Adaptive Loop
Hoàn thiện vòng:

Request
→ Analyze learner
→ Plan
→ Execute components
→ Produce artifact
→ Assess learner
→ Update LearningState
→ Next request sử dụng state mới

Đây là điểm quan trọng nhất của ALOF.

### MILESTONE 6 — API Integration
Kết nối ALOF với backend/API hiện tại.

Endpoint logic:

request
→ LearningService
→ LearningOrchestrator
→ RuntimeResult
→ response

### MILESTONE 7 — Flutter Integration
Flutter chỉ cần hiển thị:

- assistant response;
- component/agent đang hoạt động;
- artifact nếu cần;
- learning progress/state;
- quiz;
- adaptive feedback.

Không cần làm UI quá phức tạp.

### MILESTONE 8 — Demo / Documentation
Chuẩn bị một flow demo hoàn chỉnh:

1. User mới.
2. Hỏi kiến thức.
3. ALOF nhận diện intent.
4. Planner tạo workflow.
5. Research tạo artifact.
6. Mentor sử dụng artifact + learner state.
7. User làm quiz.
8. LearningState thay đổi.
9. Request tiếp theo nhận được response thích nghi.

## NGUYÊN TẮC QUAN TRỌNG

Không làm:

- benchmark mới;
- distributed coordination phức tạp;
- event bus phức tạp;
- memory system quá lớn;
- vector database nếu chưa cần;
- multi-agent communication framework phức tạp;
- LangGraph nếu chưa thực sự cần;
- abstraction nhiều tầng chỉ để "đẹp".

Ưu tiên:

**Simple → Correct → Adaptive → Demonstrable → Extensible**

## TRẠNG THÁI HIỆN TẠI

Đang ở:

Vậy thì **đừng tạo `repository.py` lúc này**. Với mục tiêu hoàn thành nhanh, repository/database cho `LearningState` là một bước quá sớm.

Ta làm **Milestone 11.1 theo bản đơn giản nhất**:

### Quyết định kiến trúc

`LearningState` hiện đã nằm trong `RuntimeContext`, nhưng Runtime được tạo **sau Planner**. Vì vậy ta cần đưa một `LearningState` vào `ExecutionRequest`.

Sửa:

```text
application/orchestration/execution_request.py
```

thêm:

```python
from backend.domain.learning.learning_state import (
    LearningState,
)
```

và:

```python
learning_state: LearningState = Field(
    default_factory=lambda: LearningState(
        learner_id="default",
    ),
)
```

Khi đó:

```text
ExecutionRequest
├── student
├── message
├── learning_state   ← thêm
└── metadata
```

Sau đó `LearningOrchestrator` truyền thẳng state sang `PlanningRequest`:

```python
planning_request = PlanningRequest(
    student=request.student,
    message=request.message,
    routing=routing_result,
    learning_state=request.learning_state,
)
```

Và đồng thời khi tạo Runtime:

```python
context = RuntimeContext.from_student(
    workflow=workflow,
    student=request.student,
)
```

sau đó gán:

```python
context.learning_state = request.learning_state
```

Như vậy **một state duy nhất được dùng xuyên suốt workflow**:

```text
ExecutionRequest
       │
       ▼
 LearningState
       │
       ├───────────────┐
       ▼               ▼
    Planner          Runtime
       │               │
       │               ▼
       │          ComponentContext
       │               │
       └──────────────► Mentor
```

### Vì sao chọn cách này?

Vì hiện tại chúng ta đang làm **MVP**, chưa cần:

```text
Database
   ↓
LearningStateRepository
   ↓
State persistence
   ↓
State reconstruction
```

Sau này khi có database thật, chỉ cần thay nguồn tạo `ExecutionRequest.learning_state` bằng state lấy từ persistence. **Planner, Workflow, Runtime và Component không cần thiết kế lại.**

### Việc tiếp theo

Tôi đề nghị làm đúng thứ tự:

**11.1**

* thêm `learning_state` vào `ExecutionRequest`;
* thêm vào `PlanningRequest`;
* truyền qua `LearningOrchestrator`;
* giữ nguyên các phần còn lại.

**11.2**

* sửa `LLMSequentialPlanner` để thực sự sử dụng state.

**11.3**

* test `LearningState → Planner → Plan`.

Đây là đường ngắn nhất để có **adaptive workflow thực sự**, không cần dựng repository ngay.
