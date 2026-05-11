import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import LocalFileStore, create_kv_docstore

MODELO_EMBEDDINGS = "mxbai-embed-large"

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")
RAG_DIR = os.path.normpath(os.path.join(BASE_DIR, "rag"))

RAG_CONFIG = {
    "equipos": {
        "carpeta": os.path.join(RAG_DIR, "equipos"),
        "collection": "equipos_tecnicos",
        "docstore": os.path.join(RAG_DIR, "store_equipos")
    },
    "presupuestos": {
        "carpeta": os.path.join(RAG_DIR, "presupuestos"),
        "collection": "presupuestos",
        "docstore": os.path.join(RAG_DIR, "store_presupuestos")
    },
    "sonido": {
        "carpeta": os.path.join(RAG_DIR, "sonido"),
        "collection": "sonido",
        "docstore": os.path.join(RAG_DIR, "store_sonido")
    }
}

CHROMA_DIR = os.path.join(RAG_DIR, "chroma_db")

def crear_embeddings():
    return OllamaEmbeddings(model=MODELO_EMBEDDINGS)

def crear_retriever(categoria: str):
    config = RAG_CONFIG[categoria]
    os.makedirs(config["docstore"], exist_ok=True)

    padre_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    hijo_splitter = RecursiveCharacterTextSplitter(chunk_size=500)

    fs = LocalFileStore(config["docstore"])
    store = create_kv_docstore(fs)

    vectorstore = Chroma(
        collection_name=config["collection"],
        embedding_function=crear_embeddings(),
        persist_directory=CHROMA_DIR
    )

    return ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=hijo_splitter,
        parent_splitter=padre_splitter,
    )

def ingest_pdfs(categoria: str = None):
    if categoria:
        _ingest_una_categoria(categoria)
    else:
        for cat in RAG_CONFIG:
            _ingest_una_categoria(cat)

def _ingest_una_categoria(categoria: str):
    config = RAG_CONFIG[categoria]
    print(f"\n{'='*50}")
    print(f"Procesando: {categoria.upper()}")
    print(f"Carpeta: {config['carpeta']}")
    print(f"{'='*50}")

    retriever = crear_retriever(categoria)

    if not os.path.exists(config["carpeta"]):
        print(f"  Carpeta no existe, creandola...")
        os.makedirs(config["carpeta"], exist_ok=True)
        print(f"  Añade PDFs a: {config['carpeta']}")
        return

    loader = PyPDFDirectoryLoader(config["carpeta"])
    docs = loader.load()

    if docs:
        retriever.add_documents(docs, ids=None)
        print(f"  [OK] {len(docs)} documentos indexados")
    else:
        print(f"  No hay PDFs en esta carpeta")

def get_retriever(categoria: str):
    return crear_retriever(categoria)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        categoria = sys.argv[1]
        print(f"Ingestando categoria: {categoria}")
        ingest_pdfs(categoria)
    else:
        print("Indice de RAG - Categorias disponibles:")
        print("="*50)
        for cat in RAG_CONFIG:
            print(f"  - {cat}")
        print("\nUsage: python -m rag.loader [categoria]")
        print("Example: python -m rag.loader equipos")
        print("         python -m rag.loader presupuestos")
        print("         python -m rag.loader sonido")
        print("         python -m rag.loader  (todas)")