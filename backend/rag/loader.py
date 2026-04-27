import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import LocalFileStore, create_kv_docstore

CHROMA_DIR = "./rag/chroma_db"
DOCSTORE_DIR = "./rag/documentos_padre"
COLLECTION_NAME = "equipos_tecnicos"
MODELO_EMBEDDINGS = "mxbai-embed-large"

def crear_embeddings():
    return OllamaEmbeddings(model=MODELO_EMBEDDINGS)

def configurar_parent_retriever():
    padre_splitter = RecursiveCharacterTextSplitter(chunk_size=1500)
    hijo_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

    if not os.path.exists(DOCSTORE_DIR): os.makedirs(DOCSTORE_DIR)
    fs = LocalFileStore(DOCSTORE_DIR)
    store = create_kv_docstore(fs)
    
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=crear_embeddings(),
        persist_directory=CHROMA_DIR
    )

    return ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=hijo_splitter,
        parent_splitter=padre_splitter,
    )

def ingest_pdfs():
    retriever = configurar_parent_retriever()
    print("Cargando PDFs de la carpeta rag/documentos_padre/")
    
    loader = PyPDFDirectoryLoader("./rag/documentos_padre")
    docs = loader.load()
    
    if docs:
        retriever.add_documents(docs, ids=None)
        print(len(docs))
    else:
        print("No se encontraron archivos PDF.")

if __name__ == "__main__":
    ingest_pdfs()