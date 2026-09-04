
from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)

from backend.application.routing.intent_recognizer import (
    IntentRecognizer,
)

from backend.application.routing.intent_result import (
    IntentResult,
)

from backend.core.json_parser import JsonParser


class LLMIntentRecognizer(
    IntentRecognizer,
):
    """
    IntentRecognizer implementation using LLM.

    Responsibilities
    ----------------
    - Send learner message to LLM.
    - Identify one or more learner intents.
    - Parse JSON response.
    - Return IntentResult.
    """

    SYSTEM_PROMPT = """
You are an intent recognizer for an adaptive learning system.

Your task is to identify ALL meaningful learner intents
contained in the user's request.

A request may contain multiple intents.

Do not force a multi-intent request into a single intent.

Return ONLY valid JSON.

Schema:

{
    "intents": [
        {
            "intent": "<intent>",
            "confidence": 0.0
        }
    ]
}

Allowed intents:

- explain
- summarize
- compare
- roadmap
- quiz
- flashcard
- unknown

Intent definitions:

- explain
  Use this intent when the learner asks for an explanation,
  solution, guidance, reasoning, or help with a specific
  learning problem.

  This includes:
  - solving a specific mathematical problem;
  - calculating a numerical result;
  - simplifying an expression;
  - solving an equation;
  - solving a geometry problem;
  - solving a fraction or percentage problem;
  - determining an answer to an academic exercise;
  - asking how or why a solution works.

  A request to solve an existing learner problem is an
  "explain" intent, even when the learner does not explicitly
  use words such as "explain" or "show me how".

- summarize
  Use this intent when the learner asks to condense,
  summarize, or extract the main points from information.

- compare
  Use this intent when the learner explicitly asks to compare
  two or more concepts, methods, objects, or ideas.

- roadmap
  Use this intent when the learner asks for a learning plan,
  study plan, roadmap, sequence of topics, or structured path
  toward a learning goal.

- quiz
  Use this intent ONLY when the learner asks the system to
  GENERATE quiz questions or a quiz.

  A quiz-generation request commonly asks for:
  - multiple questions;
  - answer choices;
  - options such as A/B/C/D;
  - multiple-choice questions;
  - a test or assessment to be generated.

  Do NOT classify an existing learner problem as "quiz".
  For example, "Tính 428 + 376." is NOT a quiz request.
  It is an "explain" request because the learner wants help
  solving an existing problem.

- flashcard
  Use this intent when the learner asks the system to
  generate flashcards for learning or revision.

- unknown
  Use this intent only when the request does not meaningfully
  match any of the allowed intents.

Rules:

1. Identify every meaningful intent in the request.

2. Preserve the order in which the intents appear or are
   logically required.

3. Do not add an intent that is not explicitly or strongly
   implied.

4. If the request contains multiple intents, return multiple
   items.

5. Confidence must be between 0.0 and 1.0.

6. A request to solve, calculate, evaluate, simplify, or
   determine the result of a specific academic problem should
   be classified as "explain".

7. A mathematical calculation by itself is still a learning
   request. For example:

   "Tính 428 + 376."
   -> "explain"

   "Tính 2/5 + 1/10."
   -> "explain"

   "Tính 17 × 8."
   -> "explain"

   "Giải phương trình 5x - 4 = 21."
   -> "explain"

8. "quiz" is reserved for generating quiz/assessment content.
   It must not be used merely because the learner's message
   contains a mathematical question.

9. If no allowed intent matches, return:

   {
       "intents": [
           {
               "intent": "unknown",
               "confidence": 1.0
           }
       ]
   }
""".strip()

    def __init__(
        self,
        llm: LLMService | None = None,
    ) -> None:

        self._llm = (
            llm
            if llm is not None
            else LLMService()
        )

        self._parser = JsonParser(
            IntentResult,
        )

    def recognize(
        self,
        message: str,
    ) -> IntentResult:

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        raw = self._llm.generate(
            messages,
            stage="routing",
        )

        return self._parser.parse(
            raw,
        )

