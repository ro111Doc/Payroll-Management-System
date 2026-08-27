"""
问题分类模块
使用 LangChain Structured Output 调用大模型，将用户问题分为四类。
"""

from typing import Literal

from pydantic import BaseModel, Field

from llm.model import get_llm
from models.user_request import UserRequest


class QuestionCategory(BaseModel):
    """问题分类结果（结构化输出，不含解释性文本）。"""

    category: Literal["salary", "other_salary", "irrelevant", "policy"] = Field(
        description=(
            "问题分类：salary=工资查询，other_salary=其他薪资查询，"
            "irrelevant=非相关问题，policy=政策查询"
        )
    )


CLASSIFY_PROMPT = """你是企业薪资智能助手的问题分类器。请根据用户问题，将其分为以下四类之一：

- salary：工资查询（查询个人工资、工资明细、工资组成、工资统计、工资发放情况等数据。包括但不限于：查询某个月工资，查询实发工资，查询岗位工资、绩效工资、补贴、扣款、保险、个税等具体金额，查询工资明细或工资组成）
- other_salary：其他薪资查询（属于薪资管理领域，但不属于当前系统支持的工资查询）
- policy：政策查询（用户询问法规、文件条文，包含但不限于： 国办发2015_18号机关事业单位职业年金办法、社会保险法、住房公积金管理条例等政策文件内容、条款释义、政策适用范围、法条规定）
- irrelevant：非相关问题（不属于工资查询，也不属于薪资政策咨询的问题，例如： 与工资、人事政策无关的问题，日常聊天，其他领域咨询）

用户问题：{query}

请以 JSON 格式输出分类结果，不要输出任何解释。
JSON 格式必须为：
{{"category": "salary"}}
其中 category 只能是 salary、other_salary、policy、irrelevant 之一。"""


class QuestionClassifier:
    """基于 LangChain LLM 的问题分类器。"""

    def __init__(self):
        self._llm = get_llm()
        self._structured_llm = self._llm.with_structured_output(
            QuestionCategory,
            method="json_mode"
        )

    def classify(self, request: UserRequest) -> QuestionCategory:
        """对用户请求中的 query 进行问题分类。

        Args:
            request: 用户请求数据模型

        Returns:
            QuestionCategory 结构化分类结果
        """
        prompt = CLASSIFY_PROMPT.format(query=request.query)
        return self._structured_llm.invoke(prompt)
