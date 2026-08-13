from backend.application.services.llm_service import LLMService


class FakeLLMProvider:

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return "test"


def test_llm_service_counts_calls():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    assert llm.call_count == 0

    llm.generate(
        [{"role": "user", "content": "A"}],
    )

    assert llm.call_count == 1

    llm.generate(
        [{"role": "user", "content": "B"}],
    )

    assert llm.call_count == 2


def test_llm_service_can_reset_call_count():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    llm.generate(
        [{"role": "user", "content": "A"}],
    )

    assert llm.call_count == 1

    llm.reset_call_count()

    assert llm.call_count == 0