"""
工资查询参数提取模块
使用 LangChain Structured Output 调用统一配置的 LLM，
从用户问题中提取工资查询所需的 6 个结构化参数，
供后续工资 HTTP 接口模块使用。
"""

from pydantic import BaseModel, Field

from llm.model import get_llm
from models.user_request import UserRequest


class SalaryQueryParams(BaseModel):
    """工资查询参数（结构化输出，不含解释性文本）。"""

    user_id: str = Field(
        description="用户编号，优先从问题中提取；问题未提供时使用默认值"
    )
    user_name: str = Field(
        description="用户姓名，优先从问题中提取；问题未提供时使用默认值"
    )
    start_month: str = Field(
        description="起始月份，两位数字，如 01；未提供默认 01",
        pattern=r"^(0[1-9]|1[0-2])$",
    )
    end_month: str = Field(
        description="截止月份，两位数字，如 12；未提供默认 12",
        pattern=r"^(0[1-9]|1[0-2])$",
    )
    year: str = Field(
        description="查询年份，四位数字；未提供默认 2026",
        pattern=r"^\d{4}$",
    )
    keywords: list[str] = Field(
        description="映射到工资报表标准字段的查询关键词，如 实发合计"
    )


EXTRACT_PROMPT = """你是企业薪资智能助手的工资查询参数解析助手。请根据用户问题，提取工资查询所需的参数。

默认值（用户问题中没有明确提供对应信息时使用）：
- 用户编号：{default_user_id}
- 用户姓名：{default_user_name}

提取规则：
1. user_id（用户编号）和 user_name（用户姓名）主要从用户问题中提取；问题中明确提供了编号或姓名时，以问题中的信息为准，否则使用默认值。不要自行编造编号、姓名或其他信息。
2. year（查询年份）使用四位数字；问题未提供年份时默认 2026。
3. start_month / end_month（起始月份 / 截止月份）使用两位数字；只问单个月份时两者相同；问月份区间时按实际起止月份填写；未提供月份时默认 01 到 12。
4. keywords（查询关键词）将用户表达映射为工资报表中的标准字段，例如“实际到账多少钱”映射为“实发合计”。工资字段范围包括：基本工资、岗位工资、薪级工资、绩效工资、补贴、津贴、奖励、各种补发、应发合计、公积金、养老保险、医疗保险、失业险、职业年金、扣款合计、应纳税所得额、应扣个税、补扣税额、实发合计等。无法确定映射时保留用户原始关键词。

用户问题：{query}

请以 JSON 格式输出提取结果，不要输出任何解释。
JSON 格式必须为：
{{"user_id": "用户编号", "user_name": "用户姓名", "start_month": "01", "end_month": "12", "year": "2026", "keywords": ["实发合计"]}}"""


class SalaryParamExtractor:
    """基于 LangChain LLM 的工资查询参数提取器。"""

    def __init__(self, llm=None):
        # 复用 model.py 中统一配置的 LLM 实例，不重复创建或配置模型
        self._llm = llm or get_llm()
        self._structured_llm = self._llm.with_structured_output(
            SalaryQueryParams,
            method="json_mode"
        )

    def extract(self, request: UserRequest) -> SalaryQueryParams:
        """从用户请求中提取工资查询参数。

        Args:
            request: 用户请求数据模型（含 query 及默认 user_code / user_name）

        Returns:
            SalaryQueryParams 结构化参数
        """
        prompt = EXTRACT_PROMPT.format(
            query=request.query,
            default_user_id=request.user_code,
            default_user_name=request.user_name,
        )
        return self._structured_llm.invoke(prompt)
