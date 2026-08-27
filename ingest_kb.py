import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

KB_DIR = "knowledge_base"
CHROMA_PATH = "chroma_kb"
COLLECTION_NAME = "company_kb"

def load_documents():
    documents = []
    for filename in os.listdir(KB_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(KB_DIR, filename)
            loader = PyPDFLoader(filepath)
            documents.extend(loader.load())
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_documents(documents)

def build_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH
    )
    return vector_store

if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} raw document pages")

    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    build_vector_store(chunks)
    print(f"Vector store saved to {CHROMA_PATH}")