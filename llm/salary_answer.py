"""
工资查询回答模块
接收用户原始问题、工资参数提取结果与工资数据解析结果，
使用 model.py 中统一配置的 LLM 生成最终自然语言回答。
本模块只负责根据已有数据生成回答，不进行工资数据计算或自行推导。
"""

from datetime import date

from llm.model import get_llm

SALARY_ANSWER_PROMPT = """你是企业薪资智能助手的工资查询回答模块。请严格依据下方提供的工资数据回答用户问题。

回答要求：
1. 严格依据工资数据回答，不得编造、修改或推测数据中没有的信息。
2. 根据用户问题筛选和组织相关数据；用户要求查询多个工资项目或多个月份时，完整返回，不能遗漏。
3. 工资数据为空或查询失败时，明确告知用户未查询到相关工资数据。
4. 使用自然、清晰的中文回答，可以使用表格。
5. 不要展示内部字段名、接口信息或程序实现细节。
6. 用户问题中出现“本月、上月、今年”等时间表达时，以当前日期为准判断对应的月份或年份，不要在回答中输出时间推导过程。
7. 只负责根据已有数据生成回答，不要进行工资数据计算或自行推导。
8. 如果查询结果包含多个月份或多份数据，必须完整输出所有相关数据，并在全部数据之后计算并输出对应的合计值。合计只能基于提供的数据进行计算，不得遗漏任何数据或自行推测。
9. 如果查询的是“实发合计”或“应发合计”，则要输出所有组成合计的部分。

当前日期：{current_date}

用户问题：{query}

查询参数：
{params}

工资数据：
{salary_data}"""


class SalaryAnswerer:
    """基于 LangChain LLM 的工资查询回答模块（复用 get_llm() 统一 LLM 实例）。"""

    def __init__(self, llm=None):
        # 复用 model.py 中统一配置的 LLM 实例，不重复创建或配置模型
        self._llm = llm or get_llm()

    def answer(self, query: str, params: dict, salary_data: dict) -> str:
        """根据工资数据生成最终自然语言回答。

        Args:
            query:       用户原始问题
            params:      工资参数提取模块输出的参数
            salary_data: 工资数据解析模块返回的完整结果

        Returns:
            最终回答文本
        """
        prompt = SALARY_ANSWER_PROMPT.format(
            current_date=date.today().strftime("%Y年%m月%d日"),
            query=query,
            params=self._format_params(params),
            salary_data=self._format_salary_data(salary_data),
        )
        response = self._llm.invoke(prompt)
        return response.content

    @staticmethod
    def _format_params(params) -> str:
        """将查询参数格式化为可读文本（不暴露内部字段名）。"""
        if not isinstance(params, dict):
            params = params.model_dump()

        lines = [
            f"查询用户：{params.get('user_name', '')}（编号：{params.get('user_id', '')}）",
            f"查询年份：{params.get('year', '')}",
            f"查询月份：{params.get('start_month', '')} 至 {params.get('end_month', '')}",
        ]

        keywords = params.get("keywords") or []
        if keywords:
            lines.append("查询关键词：" + "、".join(str(k) for k in keywords))

        return "\n".join(lines)

    @staticmethod
    def _format_salary_data(salary_data) -> str:
        """将工资解析结果格式化为可读文本。"""
        if not isinstance(salary_data, dict) or not salary_data.get("success"):
            error = (
                salary_data.get("error")
                if isinstance(salary_data, dict)
                else "未知错误"
            )
            return f"工资数据查询失败：{error}"

        records = salary_data.get("records") or []
        if not records:
            return "工资数据为空。"

        lines = []

        for record in records:

            lines.append(f"【{record.get('month', '')}】")

            for item in record.get("items", []):

                lines.append(
                    f"{item.get('name', '')}：{item.get('amount', 0):.2f}"
                )

        return "\n".join(lines)
