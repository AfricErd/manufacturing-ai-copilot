import json


def retrieve_manufacturing_knowledge(
    question: str,
    top_k: int = 3,
) -> str:
    """
    从制造业知识库中检索与问题相关的资料。

    这里只负责检索知识，
    不负责生成最终答案。

    RAG 依赖只在真正执行 Knowledge Tool 时加载，
    避免应用启动阶段初始化向量数据库。
    """

    # ========================================================
    # Lazy Import
    #
    # 只有真正调用 Knowledge Tool 时才初始化 RAG。
    # ========================================================

    from app.rag import (
        build_context,
        search,
    )

    results = search(
        question,
        top_k=top_k,
    )

    documents = (
        results["documents"][0]
    )

    metadatas = (
        results["metadatas"][0]
    )

    if not documents:

        return json.dumps(
            {
                "success": True,
                "found": False,
                "context": "",
                "sources": [],
            },
            ensure_ascii=False,
        )

    context = build_context(
        documents,
        metadatas,
    )

    sources = sorted(
        {
            metadata["source"]
            for metadata in metadatas
        }
    )

    return json.dumps(
        {
            "success": True,
            "found": True,
            "context": context,
            "sources": sources,
        },
        ensure_ascii=False,
    )