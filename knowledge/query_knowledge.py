"""
知识库检索模块
接收主流程传入的 query，检索 Chroma 向量库，
将检索到的内容全部返回给后续模块，不在此生成或打印最终回答。
"""

import json
from pathlib import Path

import chromadb


# ============================================================
# 1. 配置
# ============================================================

# 以本模块所在目录为基准，避免受程序运行目录影响
KNOWLEDGE_DIR = Path(__file__).resolve().parent

CHROMA_PATH = str(KNOWLEDGE_DIR / "chroma_db")

COLLECTION_NAME = "salary_policy"

MAPPING_FILE = str(KNOWLEDGE_DIR / "parent_child_mapping.json")


# ============================================================
# 2. 打开已有 Chroma
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


# ============================================================
# 3. 加载父子对应关系
# ============================================================

with open(
    MAPPING_FILE,
    "r",
    encoding="utf-8"
) as f:

    parent_child_mapping = json.load(f)


# ============================================================
# 4. 检索
# ============================================================

def retrieve(
    query: str,
    n_results: int = 5
) -> list:
    """根据 query 检索知识库，返回命中的完整内容（含父段）。

    Args:
        query:     用户问题
        n_results: 返回的子段数量

    Returns:
        list[dict]，每项包含 source / child_text / parent_text /
        parent_index / child_index
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    retrieved = []

    for result_id in results["ids"][0]:

        mapping = parent_child_mapping.get(
            result_id
        )

        if mapping is None:
            continue

        retrieved.append(mapping)

    return retrieved
