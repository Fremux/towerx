import chromadb
import errors
import logging
from settings import settings
from typing import List, Tuple


chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST_ADDR, port=settings.CHROMA_HOST_PORT)


def parse_input_file_class(line: str) -> Tuple[str, List[float]]:
    start_quote = line.find('"')
    end_quote = line.find('"', start_quote + 1)
    if start_quote == -1 or end_quote == -1:
        logging.error("Can't parse object class name")
        raise errors.unable_to_process_file()
    class_name = line[start_quote + 1:end_quote]
    try:
        logging.error(line[end_quote + 1:])
        embedding = list(map(float, line[end_quote + 1:].split()))
    except Exception as e:
        logging.error(f"Can't process embedding for class {class_name}")
        logging.error(e)
        raise errors.unable_to_process_file()
    return class_name, embedding


def delete_from_chroma(cls: str) -> None:
    collection = chroma_client.get_or_create_collection(name=settings.CHROMA_DB_NAME)
    result = collection.get(where={"class": cls})

    ids_to_delete = result.get("ids", [])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)


def insert_class_to_chroma(cls: List[str],
                           input_data: List[List[float]]) -> None:
    collection = chroma_client.get_or_create_collection(name=settings.CHROMA_DB_NAME)
    collection.add(
        ids=cls,
        embeddings=input_data,
        metadatas=["class"] * len(cls))


def get_all_object_classes() -> Tuple[set, int]:
    collection = chroma_client.get_or_create_collection(name=settings.CHROMA_DB_NAME)
    all_metadatas = collection.get(include=["metadatas"]).get('metadatas')
    classes = set([x.get("class") for x in all_metadatas])
    num_classes = len(classes)

    return classes, num_classes
