"""
程序入口
从命令行接收用户输入（query），经工作流（分类 → 分支处理）后，
只输出最终给用户看的回答；调试信息通过日志保留，不直接打印。
"""

import json
import logging
import nntplib
import os
import sys

from handlers.chat import handle_chat
from models.user_request import UserRequest
from workflow.router import WorkflowRouter

logger = logging.getLogger(__name__)

# 设置环境变量 SALARY_DEBUG=1 可输出完整调试日志
_DEBUG_LEVEL = logging.DEBUG if os.environ.get("SALARY_DEBUG") else logging.INFO
logging.basicConfig(
    level=_DEBUG_LEVEL,
    format="%(levelname)s %(name)s: %(message)s",
)
# 屏蔽 httpx 重复INFO日志
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    """命令行入口：读取 query → 校验 → 分类并分发 → 只输出最终回答。"""
    try:
        query = input("请输入问题 (query): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消。")
        sys.exit(0)

    # 1. /chat 接口校验输入
    result = handle_chat(query=query)

    # 2. 校验通过后进入工作流：分类 → 分支处理
    if result["success"]:
        request = UserRequest(query=query)
        router = WorkflowRouter()
        try:
            result = router.run(request)
        except Exception as e:  # 大模型调用失败等异常
            result = {"success": False, "error": f"处理失败：{e}", "data": None}

    # 完整结果记录到日志，便于调试
    logger.debug(
        "完整处理结果:\n%s",
        json.dumps(result, ensure_ascii=False, indent=2),
    )

    # 只输出最终给用户看的回答
    if result.get("success") and result.get("data"):
        print(result["data"].get("answer", ""))
    else:
        print(result.get("error") or "处理失败")

    return result


if __name__ == "__main__":
    main()
