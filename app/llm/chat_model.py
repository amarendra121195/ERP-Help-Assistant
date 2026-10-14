from langchain.chat_models import init_chat_model

from app.core import config


def get_chat_model():
    kwargs = {}
    if config.REASONING_EFFORT:
        kwargs["reasoning_effort"] = config.REASONING_EFFORT

    # gpt-5.6-luna only supports tools + reasoning_effort on the responses api
    return init_chat_model(
        config.CHAT_MODEL,
        model_provider="openai",
        use_responses_api=True,
        timeout=config.LLM_TIMEOUT,
        max_retries=config.LLM_MAX_RETRIES,
        **kwargs,
    )
