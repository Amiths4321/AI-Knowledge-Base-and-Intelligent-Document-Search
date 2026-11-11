import os

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://10.22.39.192:11434"
)

CHAT_MODEL = "qwen2.5vl:latest"

EMBEDDING_MODEL = "nomic-embed-text:latest"

CHUNK_SIZE = 500

CHUNK_OVERLAP = 75

TOP_K = 5

APP_TITLE = "AI Knowledge Base"