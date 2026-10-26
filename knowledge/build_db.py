import os

from app.vectorstore import build_index


KNOWLEDGE_PATH = "knowledge"


def main():

    pdf_files = [
        f for f in os.listdir(KNOWLEDGE_PATH)
        if f.lower().endswith(".pdf")
    ]

    print(f"发现 {len(pdf_files)} 个PDF文件")

    for pdf in pdf_files:

        pdf_path = os.path.join(KNOWLEDGE_PATH, pdf)

        print("=" * 60)
        print(f"开始处理：{pdf}")

        build_index(pdf_path)

    print("=" * 60)
    print("全部知识库构建完成！")


if __name__ == "__main__":
    main()