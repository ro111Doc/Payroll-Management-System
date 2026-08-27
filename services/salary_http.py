"""
工资查询 HTTP 请求模块
接收工资参数提取模块输出的参数，构造请求体调用内部工资接口。
本模块只负责发送请求并返回 status_code 和 body，不解析工资数据。
"""

import time

import requests

from config.settings import settings


# ============================================================
# 1. 接口配置
# ============================================================

SALARY_API_URL = "http://192.168.1.203:1024/ureport/ureport/loadData"

# 报表名称（请求体中固定）
REPORT_NAME = "机电UReport报表/工资管理/个人工资查询(全校).fine.ureport.xml"

# 请求失败后自动重试次数（不含首次请求）
MAX_RETRIES = 3

# 重试间隔（秒）
RETRY_INTERVAL = 1

# 单次请求超时（秒）
REQUEST_TIMEOUT = 10

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "http://192.168.1.203:1024",
    "Referer": "http://192.168.1.203:1024/udr-web/index.html",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    ),
}


# ============================================================
# 2. 构造请求体
# ============================================================

def _build_body(
    user_name: str,
    start_month: str,
    end_month: str,
    year: str
) -> dict:
    """按内部接口格式构造请求 Body。

    sso_token 填入 authorization 配置，
    login_year / IDEN_NAME / month_start / month_end 填入查询参数。
    """
    return {
        "pageIndex": 1,
        "params": {
            "reportName": REPORT_NAME,
            "content": "",
            "query": {
                "fileId": REPORT_NAME,
                "subId": settings.authorization_id,
                "sso_token": settings.authorization,
                "role_id": settings.authorization_roleid,
                "user_id": "1",
                "login_year": year,
                "area_code": "",
                "en_code": "",
                "mb_code": "",
                "IDEN_NAME": [user_name],
                "month_start": start_month,
                "month_end": end_month,
                "pageSize": None,
                "searchId": "2",
                "sheetIndex": 1,
            },
        },
    }


# ============================================================
# 3. 发起请求
# ============================================================

def fetch_salary(
    user_name: str,
    start_month: str,
    end_month: str,
    year: str
) -> dict:
    """调用内部工资接口查询个人工资，请求失败自动重试。

    Args:
        user_name:   用户姓名
        start_month: 起始月份（两位数字）
        end_month:   截止月份（两位数字）
        year:        查询年份（四位数字）

    Returns:
        dict: {"success": bool, "status_code": int|None,
               "body": str|None, "error": str|None}
        只返回原始 status_code 和 body，不在此解析工资数据。
    """
    body = _build_body(
        user_name=user_name,
        start_month=start_month,
        end_month=end_month,
        year=year,
    )

    last_error = None

    for attempt in range(MAX_RETRIES + 1):

        try:

            response = requests.get(
                SALARY_API_URL,
                headers=HEADERS,
                json=body,
                timeout=REQUEST_TIMEOUT,
            )

            return {
                "success": True,
                "status_code": response.status_code,
                "body": response.text,
                "error": None,
            }

        except requests.RequestException as e:

            last_error = str(e)

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_INTERVAL)

    return {
        "success": False,
        "status_code": None,
        "body": None,
        "error": last_error,
    }
