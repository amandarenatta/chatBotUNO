import os
from dotenv import load_dotenv

load_dotenv()

# Caminhos de arquivos e pastas
PDF_PATH = os.path.join("pdf", "uno.pdf")
DB_FAISS_PATH = os.path.join("data", "faiss_index_uno")

# Configurações de chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Modelo de LLM 
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Embedding Model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_google_api_key():
    return os.getenv("GOOGLE_API_KEY")
