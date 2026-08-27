"""
政策问答模块
接收用户原始 query 与知识库检索到的父段内容，
使用 model.py 中统一配置的 LLM，严格依据知识库内容回答政策问题。
"""

from llm.model import get_llm

POLICY_QA_PROMPT = """你是企业工资管理系统的人事政策法规解读助手。请严格依据下方提供的知识库内容回答用户问题。

要求：
1. 只能使用知识库内容回答，答案优先以检索到的政策原文为依据，可以适当通俗解读，但不能篡改法条、文件原文含义，不得编造知识库中没有的信息，不得超出知识库内容进行推测或补充。
3. 如果知识库内容不足以回答问题，请明确说明知识库中未找到相关信息，不要猜测。
4. 回答准确、简洁，可引用知识库原文。回答中可以标注对应文件名称。
5. 区分政策条文与本地工资执行标准：政策只规定框架规则，不要擅自做测算；薪资测算请引导用户咨询工资相关业务。 
6. 客观中立解读法规，不做超出文件范围的延伸解读，不创造政策不存在的条款。涉及政策名称、时间、金额、比例等信息时，保持准确。

知识库内容：
{context}

用户问题：{query}"""


class PolicyQA:
    """基于知识库的政策问答模块（复用 get_llm() 统一 LLM 实例）。"""

    def __init__(self, llm=None):
        # 复用 model.py 中统一配置的 LLM 实例，不重复创建
        self._llm = llm or get_llm()

    def answer(self, query: str, retrieved_chunks: list) -> str:
        """根据知识库检索结果回答政策问题。

        Args:
            query:           用户原始问题
            retrieved_chunks: query_knowledge.retrieve 返回的检索内容列表

        Returns:
            最终回答文本
        """
        prompt = POLICY_QA_PROMPT.format(
            context=self._format_context(retrieved_chunks),
            query=query,
        )
        response = self._llm.invoke(prompt)
        return response.content

    @staticmethod
    def _format_context(retrieved_chunks: list) -> str:
        """将检索内容格式化为提示词中的上下文。"""
        parts = []

        for index, chunk in enumerate(retrieved_chunks, start=1):

            parts.append(
                f"【片段 {index}】来源：{chunk.get('source', '')}\n"
                f"{chunk.get('parent_text', '')}"
            )

        return "\n\n".join(parts)
