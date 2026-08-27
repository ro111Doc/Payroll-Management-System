"""
用户请求数据模型
"""

from dataclasses import dataclass

# 默认值：后续流程步骤可能会修改这两个值
DEFAULT_USER_CODE = "137570508"
DEFAULT_USER_NAME = "秦镟艳"


@dataclass
class UserRequest:
    """用户请求数据模型。

    Attributes:
        query:     用户问题（当前由用户输入）
        user_code: 职员代码（默认值，后续步骤可能修改）
        user_name: 用户姓名（默认值，后续步骤可能修改）
    """

    query: str
    user_code: str = DEFAULT_USER_CODE
    user_name: str = DEFAULT_USER_NAME

    def validate(self) -> str | None:
        """校验必填字段是否为空（当前仅 query 必填）。

        Returns:
            校验通过返回 None，否则返回错误信息字符串。
        """
        if not self.query or not self.query.strip():
            return "query 不能为空"
        return None

    def to_dict(self) -> dict:
        """转为字典。"""
        return {
            "user_code": (self.user_code or "").strip(),
            "user_name": (self.user_name or "").strip(),
            "query": self.query.strip(),
        }
