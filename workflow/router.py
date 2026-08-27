"""
工作流路由模块
根据问题分类结果，将用户请求分发到对应的处理分支。
分支逻辑只放在这里，QuestionClassifier 只负责分类。
"""

from llm.classifier import QuestionClassifier
from models.user_request import UserRequest

# 固定提示文案
OTHER_SALARY_MESSAGE = (
    "当前的问题属于其他薪资管理范围。当前助手仅支持校级工资相关信息查询，"
    "无法回答其他类型的问题。"
)

IRRELEVANT_MESSAGE = (
    "当前的问题不属于工资管理、其他薪资管理或相关政策查询范围。"
    "当前助手仅支持工资、其他薪资和相关政策查询，无法回答其他类型的问题。"
)

# 知识库无检索结果时的固定回复
POLICY_NO_RESULT_MESSAGE = "知识库中未找到与问题相关的政策内容，无法回答。"


class WorkflowRouter:
    """工作流路由器：分类 → 分支处理 → 返回结果。"""

    def __init__(self, classifier: QuestionClassifier | None = None):
        self._classifier = classifier or QuestionClassifier()

    def run(self, request: UserRequest) -> dict:
        """执行工作流，返回最终 JSON 结果。

        Args:
            request: 用户请求数据模型

        Returns:
            包含 success 状态和分支处理结果的 dict
        """
        category = self._classifier.classify(request)
        return self._dispatch(self._extract_category(category), request)

    @staticmethod
    def _extract_category(result) -> str:
        """提取分类值（兼容 Pydantic 对象和 dict 两种返回形式）。"""
        if isinstance(result, dict):
            return result["category"]
        return result.category

    def _dispatch(self, category: str, request: UserRequest) -> dict:
        """按分类分发到对应分支。"""
        branches = {
            "salary": self._salary_branch,
            "policy": self._policy_branch,
            "other_salary": self._other_salary_branch,
            "irrelevant": self._irrelevant_branch,
        }
        handler = branches.get(category)
        if handler is None:
            return {
                "success": False,
                "error": f"未知的问题分类：{category}",
                "data": None,
            }
        return handler(request)

    def _salary_branch(self, request: UserRequest) -> dict:
        """salary：LLM 提取工资查询参数 → 调用内部工资 HTTP 接口 → 解析工资数据 → LLM 生成最终回答。"""
        # 延迟导入：仅在 salary 分支需要时加载
        from llm.salary_params import SalaryParamExtractor
        from services.salary_http import fetch_salary
        from services.salary_parser import parse_salary_html

        params = SalaryParamExtractor().extract(request)

        # 兼容 Pydantic 对象和 dict 两种返回形式
        if isinstance(params, dict):
            params_data = params
        else:
            params_data = params.model_dump()

        http_result = fetch_salary(
            user_name=params_data["user_name"],
            start_month=params_data["start_month"],
            end_month=params_data["end_month"],
            year=params_data["year"],
        )

        if http_result["success"]:
            salary_data = parse_salary_html(
                http_result["body"],
                user_id=params_data["user_id"],
                user_name=params_data["user_name"],
            )
        else:
            salary_data = {
                "success": False,
                "error": http_result["error"],
                "header": [],
                "records": [],
            }

        # LLM 根据工资数据生成最终回答（数据为空或查询失败时也会生成提示）
        from llm.salary_answer import SalaryAnswerer

        answer = SalaryAnswerer().answer(
            query=request.query,
            params=params_data,
            salary_data=salary_data,
        )

        return {
            "success": True,
            "error": None,
            "data": {
                "category": "salary",
                "module": "salary_query",
                "status": "done",
                "params": params_data,
                "http": http_result,
                "salary_data": salary_data,
                "answer": answer,
            },
        }

    def _policy_branch(self, request: UserRequest) -> dict:
        """policy：知识库检索 → LLM 依据知识库回答 → 输出最终回答。"""
        # 延迟导入：仅在 policy 分支需要时加载知识库模块
        from knowledge.query_knowledge import retrieve
        from llm.policy_qa import PolicyQA

        retrieved_chunks = retrieve(request.query)

        if retrieved_chunks:
            answer = PolicyQA().answer(request.query, retrieved_chunks)
        else:
            answer = POLICY_NO_RESULT_MESSAGE

        return {
            "success": True,
            "error": None,
            "data": {
                "category": "policy",
                "module": "policy_consult",
                "status": "done",
                "answer": answer,
            },
        }

    def _other_salary_branch(self, request: UserRequest) -> dict:
        """other_salary：直接返回固定提示，流程结束。"""
        return {
            "success": True,
            "error": None,
            "data": {
                "category": "other_salary",
                "module": None,
                "status": "done",
                "answer": OTHER_SALARY_MESSAGE,
            },
        }

    def _irrelevant_branch(self, request: UserRequest) -> dict:
        """irrelevant：直接返回固定提示，流程结束。"""
        return {
            "success": True,
            "error": None,
            "data": {
                "category": "irrelevant",
                "module": None,
                "status": "done",
                "answer": IRRELEVANT_MESSAGE,
            },
        }
