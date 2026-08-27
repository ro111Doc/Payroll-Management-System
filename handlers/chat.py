"""
/chat 接口处理模块
负责接收用户请求、校验字段、返回 JSON 结果。
"""

from models.user_request import DEFAULT_USER_CODE, DEFAULT_USER_NAME, UserRequest


def handle_chat(
    query: str,
    user_code: str = DEFAULT_USER_CODE,
    user_name: str = DEFAULT_USER_NAME,
) -> dict:
    """处理 /chat 请求：校验输入并返回结果。

    Args:
        query:     用户问题（必填）
        user_code: 职员代码（带默认值，后续流程可能修改）
        user_name: 用户姓名（带默认值，后续流程可能修改）

    Returns:
        JSON 格式的 dict，包含 success 状态和相关信息。
    """
    # 构建请求模型
    request = UserRequest(
        query=query,
        user_code=user_code,
        user_name=user_name,
    )

    # 校验必填字段
    error = request.validate()
    if error:
        return {
            "success": False,
            "error": error,
            "data": None,
        }

    # 校验通过，返回确认信息（业务逻辑后续扩展）
    return {
        "success": True,
        "error": None,
        "data": {
            "message": "请求已接收",
            **request.to_dict(),
        },
    }
