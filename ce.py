from services .salary_http import fetch_salary


def main():
    print("=" * 60)
    print("工资接口 HTTP 请求测试")
    print("=" * 60)

    # 测试参数
    user_id = input("请输入职员代码：").strip()
    user_name = input("请输入职员姓名：").strip()
    year = input("请输入年份（如 2026）：").strip()
    start_month = input("请输入起始月份（如 01）：").strip()
    end_month = input("请输入结束月份（如 12）：").strip()

    print("\n正在请求工资接口，请稍候...\n")

    result = fetch_salary(
        user_name=user_name,
        year=year,
        start_month=start_month,
        end_month=end_month,
    )

    print("=" * 60)
    print("请求结果")
    print("=" * 60)

    print("success:", result["success"])
    print("status_code:", result["status_code"])
    print("error:", result["error"])

    print("\n" + "=" * 60)
    print("接口原始返回内容")
    print("=" * 60)

    if result["body"]:
        print(result["body"])
    else:
        print("没有返回内容")


if __name__ == "__main__":
    main()