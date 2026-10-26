import os

import chromadb

from app.embedding import get_embedding
from app.loader import load_pdf
from app.loader import split_text

client = chromadb.PersistentClient(
    path="data/chroma"
)

collection = client.get_or_create_collection(
    name="manufacturing"
)

def build_index(pdf_path):

    # 获取PDF文件名
    filename = os.path.basename(pdf_path)

    # 读取PDF
    text = load_pdf(pdf_path)

    # 切分文本
    chunks = split_text(text)

    # 遍历Chunk
    for i, chunk in enumerate(chunks):

        # 获取Embedding
        embedding = get_embedding(chunk)

        # 生成唯一ID
        chunk_id = f"{filename}_{i}"
        try:

            collection.delete(ids=[chunk_id])

        except Exception:

            pass

        # 保存到Chroma
        collection.add(

                ids=[chunk_id],

                embeddings=[embedding],

                documents=[chunk],

                metadatas=[
                    {
                        "source": filename,
                        "chunk": i
                    }
                ]

            )

    print(f"{filename} 建库完成，共 {len(chunks)} 个Chunk")

    print("建库完成！")