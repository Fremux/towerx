import pickle, chromadb
from tqdm import tqdm

with open("chroma_result.pth", "rb") as file:
    data = pickle.load(file)

client = chromadb.HttpClient(host="62.169.159.176", port=28001)
client.delete_collection("towers")
collection = client.get_or_create_collection("towers")

ids = []
embs = []
metadatas = []
for row in data:
    embs.append(row["embeddings"][0])
    ids.append(row['ids'])
    metadatas.append(row["metadatas"])
collection.upsert(
    embeddings=embs,
    ids=ids,
    metadatas=metadatas,
)
print(embs[0])