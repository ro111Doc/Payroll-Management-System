from services.salary_http import fetch_salary
from services.salary_parser import parse_salary_html


def main():
    print("=" * 60)
    print("工资查询完整测试")
    print("=" * 60)

    user_name = input("请输入职员姓名：").strip()
    year = input("请输入年份（如 2026）：").strip()
    start_month = input("请输入起始月份（如 01）：").strip()
    end_month = input("请输入结束月份（如 12）：").strip()

    # ============================================================
    # 第一步：调用 HTTP 接口
    # ============================================================

    print("\n正在请求工资接口...")

    response = fetch_salary(
        user_name=user_name,
        start_month=start_month,
        end_month=end_month,
        year=year,
    )

    print("\nHTTP 请求完成")
    print("success:", response["success"])
    print("status_code:", response["status_code"])

    if not response["success"]:
        print("HTTP 请求失败：")
        print(response["error"])
        return

    body = response["body"]

    print("收到原始数据，长度：", len(body))
    print("原始数据前 300 个字符：")
    print(body[:300])

    # ============================================================
    # 第二步：解析 HTTP 返回的 HTML
    # ============================================================

    print("\n正在解析工资数据...")

    result = parse_salary_html(body)

    # ============================================================
    # 第三步：输出解析结果
    # ============================================================

    print("\n" + "=" * 60)
    print("解析结果")
    print("=" * 60)

    print("success:", result["success"])

    if not result["success"]:
        print("解析失败：", result["error"])
        return

    records = result["records"]

    print("共解析到", len(records), "个月份的数据")

    for record in records:
        print("\n" + "-" * 40)
        print("【" + record["month"] + "】")

        for item in record["items"]:
            print(
                item["name"],
                "：",
                item["amount"]
            )


if __name__ == "__main__":
    main()