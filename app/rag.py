import chromadb

from app.embedding import get_embedding

client = chromadb.PersistentClient(
    path="data/chroma"
)

collection = client.get_collection(
    name="manufacturing"
)

def search(question, top_k=3,threshold=1.0):

    embedding = get_embedding(question)

    results = collection.query(

        query_embeddings=[embedding],

        n_results=top_k

    )




    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # ============================================================
    # 简洁 RAG 日志
    #
    # 不输出完整知识库内容，只记录：
    # - 查询内容
    # - 召回数量
    # - 最佳距离
    # - 来源
    # ============================================================

    sources = []

    for metadata in metadatas:

        source = metadata.get(
            "source",
            "unknown",
        )

        if source not in sources:
            sources.append(source)


    best_distance = None

    if distances:
        best_distance = min(
            distances
        )


    print(
        "[RAG]",
        f"query={question!r}",
        f"retrieved={len(documents)}",
        f"best_distance={best_distance}",
        f"sources={sources}",
    )



    filtered_documents = []
    filtered_metadatas = []
    filtered_distances = []
    for doc, meta, distance in zip(documents, metadatas, distances):

        if distance < threshold:

            filtered_documents.append(doc)

            filtered_metadatas.append(meta)

            filtered_distances.append(distance)
    
    print(
    "[RAG]",
    f"accepted={len(filtered_documents)}",
    f"threshold={threshold}",
    )

    results["documents"][0] = filtered_documents
    results["metadatas"][0] = filtered_metadatas
    results["distances"][0] = filtered_distances
    return results

def build_context(documents, metadatas):
    context_parts = []

    for  i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        context_parts.append(f'''召回资料{i}: \n\n来源：{meta['source']}\n\n内容： {doc}''')

    return "\n\n".join (context_parts)


