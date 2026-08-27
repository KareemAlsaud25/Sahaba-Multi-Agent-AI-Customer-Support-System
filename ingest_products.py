import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PRODUCTS_PATH = "data/products.csv"
CHROMA_PATH = "chroma_products"
COLLECTION_NAME = "products_kb"

def load_products():
    return pd.read_csv(PRODUCTS_PATH)

def build_product_documents(df):
    documents = []
    for _, row in df.iterrows():
        content = (
            f"Product name: {row['product_name']}. "
            f"Category: {row['category']}. "
            f"Price: {row['price']}. "
            f"Rating: {row['rating']}. "
            f"Stock: {row['stock']}. "
            f"Description: {row['description']}."
        )
        metadata = {
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "price": row["price"],
            "rating": row["rating"],
            "stock": row["stock"]
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

def build_vector_store(documents):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH
    )
    return vector_store

if __name__ == "__main__":
    df = load_products()
    print(f"Loaded {len(df)} products")

    docs = build_product_documents(df)
    print(f"Built {len(docs)} product documents")

    build_vector_store(docs)
    print(f"Vector store saved to {CHROMA_PATH}")