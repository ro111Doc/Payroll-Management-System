import json
from pathlib import Path

import chromadb
from langchain_docling.loader import DoclingLoader


# ============================================================
# 1. 配置
# ============================================================

DOCX_DIR = Path(r"F:\train\docx")

MAPPING_FILE = Path("parent_child_mapping.json")

CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "salary_policy"


# ============================================================
# 2. 创建 Chroma
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# 3. 获取三个 DOCX 文件
# ============================================================

docx_files = [
    DOCX_DIR / "住房公积金管理条例_司法部行政法规库.docx",
    DOCX_DIR / "国办发2015_18号_机关事业单位职业年金办法.docx",
    DOCX_DIR / "中华人民共和国社会保险法_2018修正.docx",
]


# ============================================================
# 4. 保存父段 / 子段对应关系
# ============================================================

parent_child_mapping = {}

# 所有需要进入 Chroma 的子段
child_documents = []

# 所有子段 ID
child_ids = []

child_id = 1
parent_count = 0

# ============================================================
# 5. 逐个处理三个文件
# ============================================================

for file_path in docx_files:

    print("=" * 60)
    print(f"正在处理：{file_path.name}")

    # --------------------------------------------------------
    # 设置空变量 text_field
    # --------------------------------------------------------

    text_field = ""

    # --------------------------------------------------------
    # Docling 加载文档
    # --------------------------------------------------------

    loader = DoclingLoader(
        file_path=str(file_path)
    )

    documents = loader.load()

    # --------------------------------------------------------
    # 将 Document 内容放入 text_field
    # --------------------------------------------------------

    for document in documents:

        text_field += document.page_content

    # --------------------------------------------------------
    # AAAAAAAAAA：划分父段
    # --------------------------------------------------------

    parent_sections = text_field.split("AAAAAAAAAA")

    parent_sections = [
        parent.strip()
        for parent in parent_sections
        if parent.strip()
    ]

    # 累加当前文件的父段数量
    parent_count += len(parent_sections)

    print(f"父段数量：{len(parent_sections)}")

    # --------------------------------------------------------
    # BBBBBBBBB：划分子段
    # --------------------------------------------------------

    for parent_index, parent_text in enumerate(
        parent_sections
    ):

        child_sections = parent_text.split(
            "BBBBBBBBB"
        )

        child_sections = [
            child.strip()
            for child in child_sections
            if child.strip()
        ]

        for child_index, child_text in enumerate(
            child_sections
        ):

            current_child_id = f"child_{child_id}"

            # ------------------------------------------------
            # 子段进入 Chroma
            # ------------------------------------------------

            child_documents.append(
                child_text
            )

            child_ids.append(
                current_child_id
            )

            # ------------------------------------------------
            # 保存子段 -> 父段关系
            # ------------------------------------------------

            parent_child_mapping[
                current_child_id
            ] = {

                "child_text": child_text,

                "parent_text": parent_text,

                "parent_index": parent_index,

                "child_index": child_index,

                "source": file_path.name,
            }

            child_id += 1


# ============================================================
# 6. 保存父子对应关系
# ============================================================

MAPPING_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    MAPPING_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        parent_child_mapping,
        f,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# 7. 将所有子段写入 Chroma
# ============================================================

collection.upsert(
    documents=child_documents,
    ids=child_ids
)


# ============================================================
# 8. 输出结果
# ============================================================

print("\n" + "=" * 60)
print("知识库建立完成")
print("=" * 60)

print(f"处理文件数量：{len(docx_files)}")

print(f"父段数量：{parent_count}")

print(f"子段数量：{len(child_documents)}")

print(f"Chroma位置：{CHROMA_PATH}")

print(f"父子关系：{MAPPING_FILE}")