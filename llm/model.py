"""
LLM 统一配置与创建模块
所有调用大模型的地方统一从这里获取 LLM 实例。
"""

from functools import lru_cache

from langchain.chat_models import init_chat_model

from config.settings import settings


@lru_cache(maxsize=1)
def get_llm():
    """创建（或复用）全局唯一的 LangChain LLM 实例。

    配置项来自 config/settings.py，避免各处重复配置。
    """
    return init_chat_model(
        settings.llm_model,
        model_provider="deepseek",
        api_key=settings.llm_api_key,
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout,
        max_tokens=settings.llm_max_tokens,
    )
