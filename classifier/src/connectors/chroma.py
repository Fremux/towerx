import chromadb
from settings import settings


client = chromadb.HttpClient(host=settings.CHROMA_HOST_ADDR, port=settings.CHROMA_HOST_PORT)
collection = client.get_or_create_collection(settings.CHROMA_DB_NAME)
