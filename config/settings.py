"""
系统固定配置模块
存放后续用于调用内部工资接口的配置项，不暴露给用户输入。
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """系统固定配置，后续用于调用内部工资接口。"""

    # 内部工资接口认证信息
    authorization: str = os.getenv("SALARY_AUTHORIZATION", "")
    authorization_code: str = os.getenv("SALARY_AUTHORIZATION_CODE", "01")
    authorization_id: str = os.getenv(
        "SALARY_AUTHORIZATION_ID",
        "172d762fdc864215a2ddbe5ca8011c58"
    )
    authorization_roleid: str = os.getenv("SALARY_AUTHORIZATION_ROLEID", "2")

    # 内部接口基础 URL
    base_url: str = os.getenv("SALARY_BASE_URL", "")

    # 大模型配置（用于问题分类等场景）
    llm_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    llm_base_url: str = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com/anthropic"
    )
    llm_model: str = os.getenv(
        "DEEPSEEK_MODEL",
        "deepseek-v4-flash"
    )
    llm_temperature: float = float(
        os.getenv("DEEPSEEK_TEMPERATURE", "0")
    )
    llm_timeout: int = int(
        os.getenv("DEEPSEEK_TIMEOUT", "60")
    )
    llm_max_tokens: int = int(
        os.getenv("DEEPSEEK_MAX_TOKENS", "1024")
    )

    def dict(self) -> dict:
        """返回所有配置项的字典（隐藏敏感字段值）。"""
        return {
            "authorization": "***" if self.authorization else "(empty)",
            "authorization_code": "***" if self.authorization_code else "(empty)",
            "authorization_id": self.authorization_id or "(empty)",
            "authorization_roleid": self.authorization_roleid or "(empty)",
            "base_url": self.base_url or "(empty)",
        }


# 全局配置单例
settings = Settings()
