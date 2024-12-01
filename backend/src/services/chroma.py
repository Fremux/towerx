import chromadb
from settings import settings
from typing import List


def delete_from_chroma(cls: int) -> None:
    chroma_client = chromadb.HttpClient(host=settings.CHROMADB_URL, port=settings.CHROMADB_PORT)
    collection = chroma_client.get_or_create_collection(name=settings.CHROMADB_NAME)
    result = collection.fetch(where={"class": cls})

    ids_to_delete = result.get("ids", [])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)


def insert_to_chroma(cls: int,
                     input_data: List[float]) -> None:
    chroma_client = chromadb.HttpClient(host=settings.CHROMADB_URL, port=settings.CHROMADB_PORT)
    collection = chroma_client.get_or_create_collection(name=settings.CHROMADB_NAME)
    collection.add(
        ids=[cls],
        embeddings=[input_data],
        metadatas=["class"]
    )
