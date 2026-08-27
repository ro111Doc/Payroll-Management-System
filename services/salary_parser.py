"""
工资数据解析模块
解析工资 HTTP 接口返回的 HTML（UReport 报表），
提取发放月份与各工资项目金额，只保留非零数据。
本模块只负责解析和整理数据，不回答用户问题，不调用 LLM。
"""

import re
from html.parser import HTMLParser

# 关键列名（精确匹配）
CODE_COLUMN = "职员代码"
NAME_COLUMN = "职员姓名"
MONTH_COLUMN = "发放月份"
ITEM_START_COLUMN = "岗位"


# ============================================================
# 1. HTML 表格解析器
# ============================================================

class _TableParser(HTMLParser):
    """提取 HTML 中所有表格的行与单元格文本。"""

    def __init__(self):
        super().__init__()

        self.tables = []

        self.table = []
        self.row = []
        self.cell = ""

        self.in_table = False
        self.in_row = False
        self.in_cell = False

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()

        if tag == "table":

            self.in_table = True
            self.table = []

        elif tag == "tr" and self.in_table:

            self.in_row = True
            self.row = []

        elif tag in ["td", "th"] and self.in_row:

            self.in_cell = True
            self.cell = ""

    def handle_data(self, data):

        if self.in_cell:
            self.cell += data

    def handle_entityref(self, name):

        # 处理 &nbsp; 等实体，避免其混入单元格文本
        entities = {
            "nbsp": " ", "amp": "&", "lt": "<",
            "gt": ">", "quot": '"', "apos": "'",
        }

        if self.in_cell:
            self.cell += entities.get(name, "")

    def handle_charref(self, name):

        if self.in_cell:

            try:

                if name.startswith("x"):
                    self.cell += chr(int(name[1:], 16))
                else:
                    self.cell += chr(int(name))

            except ValueError:
                pass

    def handle_endtag(self, tag):

        tag = tag.lower()

        if tag in ["td", "th"]:

            if self.in_cell:

                value = re.sub(
                    r"\s+",
                    " ",
                    self.cell
                ).strip()

                self.row.append(value)

                self.in_cell = False

        elif tag == "tr":

            if self.in_row:

                if self.row:
                    self.table.append(
                        self.row
                    )

                self.in_row = False

        elif tag == "table":

            if self.table:
                self.tables.append(
                    self.table
                )

            self.in_table = False


# ============================================================
# 2. 金额转换
# ============================================================

def _clean_number(value):
    """金额处理：空值 → 0，去除逗号，非数字 → 0。"""

    value = value.strip()

    if value == "":
        return 0

    value = value.replace(",", "")

    try:
        return float(value)
    except ValueError:
        return 0


# ============================================================
# 3. 解析工资数据
# ============================================================

def parse_salary_html(body, user_id=None, user_name=None):
    """解析工资 HTTP 接口返回的原始 HTML。

    Args:
        body:      HTTP 模块返回的原始响应内容（HTML 字符串）
        user_id:   可选，用于按职员代码过滤
        user_name: 可选，用于按职员姓名过滤

    Returns:
        dict: {"success": bool, "error": str|None, "header": list,
               "records": [{"month": str,
                            "items": [{"name": str, "amount": float}]}]}
        每个 records 项明确标注发放月份；一行中多个非零项目全部保留。
    """
    # 1. 空响应
    if not body or not body.strip():
        return {
            "success": False,
            "error": "响应内容为空，未找到工资数据",
            "header": [],
            "records": [],
        }

    parser = _TableParser()

    parser.feed(body)

    # 2. 找工资表：包含 职员代码 / 职员姓名 / 发放月份 的表
    target_table = None

    for table in parser.tables:

        text = " ".join(
            [
                " ".join(row)
                for row in table
            ]
        )

        if (
            CODE_COLUMN in text
            and
            NAME_COLUMN in text
            and
            MONTH_COLUMN in text
        ):

            target_table = table
            break

    if target_table is None:
        return {
            "success": False,
            "error": "没有找到工资数据表",
            "header": [],
            "records": [],
        }

    # 3. 找表头行：包含 职员代码 和 职员姓名
    header_index = -1
    headers = []

    for i, row in enumerate(target_table):

        if (
            CODE_COLUMN in row
            and
            NAME_COLUMN in row
        ):

            header_index = i
            headers = row
            break

    if header_index == -1:
        return {
            "success": False,
            "error": "没有找到表头",
            "header": [],
            "records": [],
        }

    # 4. 找关键列（精确匹配）
    def find_col(name):

        for i, h in enumerate(headers):

            if h.strip() == name:
                return i

        return -1

    code_col = find_col(CODE_COLUMN)
    name_col = find_col(NAME_COLUMN)
    month_col = find_col(MONTH_COLUMN)
    salary_start = find_col(ITEM_START_COLUMN)

    if month_col == -1:
        return {
            "success": False,
            "error": "表头中未找到“发放月份”列",
            "header": headers,
            "records": [],
        }

    if salary_start == -1:
        return {
            "success": False,
            "error": "没有找到工资项目区域（缺少“岗位”列）",
            "header": headers,
            "records": [],
        }

    # 5. 筛选该用户的记录（行太短跳过；可选按职员代码/姓名过滤）
    min_columns = max(code_col, name_col, month_col, salary_start)

    filtered_rows = []

    for row in target_table[header_index + 1:]:

        if len(row) <= min_columns:
            continue

        code = (
            row[code_col].strip()
            if code_col < len(row)
            else ""
        )

        name = (
            row[name_col].strip()
            if name_col < len(row)
            else ""
        )

        if user_id is not None and str(user_id) not in code:
            continue

        if user_name is not None and user_name not in name:
            continue

        filtered_rows.append(row)

    if not filtered_rows:

        if user_id is not None or user_name is not None:
            error = "未找到该用户工资记录"
        else:
            error = "未找到有效工资数据行"

        return {
            "success": False,
            "error": error,
            "header": headers,
            "records": [],
        }

    # 6. 逐行提取工资项目（只保留非零数据，标注发放月份）
    records = []

    for row in filtered_rows:

        month = (
            row[month_col].strip()
            if month_col < len(row)
            else ""
        )

        # 没有发放月份的行无法标注月份，跳过
        if not month:
            continue

        items = []

        for i in range(salary_start, len(headers)):

            if i >= len(row):
                continue

            item_name = headers[i].strip()
            if not item_name:
                continue

            number = _clean_number(row[i])

            # 只保留非零工资数据
            if number != 0:
                items.append({
                    "name": item_name,
                    "amount": number,
                })

        # 每行（每个月份）的多个非零项目全部保留
        if items:
            records.append({
                "month": month,
                "items": items,
            })

    if not records:
        return {
            "success": False,
            "error": "未找到有效的非零工资数据",
            "header": headers,
            "records": [],
        }

    return {
        "success": True,
        "error": None,
        "header": headers,
        "records": records,
    }
