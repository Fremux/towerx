import chromadb
from settings import settings


def delete_from_chroma(cls: int):
    chroma_client = chromadb.HttpClient(host=settings.CHROMADB_URL, port=settings.CHROMADB_PORT)
    collection = chroma_client.get_or_create_collection(name=settings.CHROMADB_NAME)
    result = collection.fetch(where={"class": cls})

    ids_to_delete = result.get("ids", [])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
