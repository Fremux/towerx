from pathlib import Path
import os

WEIGHTS_DIR = Path("../weights")
CHROMADB_URL = os.getenv("CHROMADB_URL", "62.169.159.176")
CHROMADB_PORT = os.getenv("CHROMADB_PORT", "28001")
CHROMADB_NAME = os.getenv("CHROMADB_NAME", "towers")
TOP_K = os.getenv("TOP_K", 10)
os.environ["HF_HOME"] = str(WEIGHTS_DIR.absolute())

from io import BytesIO
from schema import BBoxResult, Bbox
from transformers import CLIPModel, CLIPProcessor, CLIPConfig
from PIL import Image
from tqdm import tqdm
from collections import Counter

import torch, chromadb, requests

# os.environ("TRANSFORMERS_CACHE") = str(WEIGHTS_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

client = chromadb.HttpClient(host=CHROMADB_URL, port=int(CHROMADB_PORT))
collection = client.get_or_create_collection(CHROMADB_NAME)

model_id = "zer0int/CLIP-GmP-ViT-L-14"
config = CLIPConfig.from_pretrained(model_id)
processor = CLIPProcessor.from_pretrained(model_id)
model = CLIPModel.from_pretrained(model_id).to(device)
model.eval()

def crop_image(image, x_center, y_center, width, height):
    # Get image dimensions
    image_width, image_height = image.size
    
    # Calculate pixel coordinates
    x_min = x_center * image_width - (width * image_width) / 2
    y_min = y_center * image_height - (height * image_height) / 2
    x_max = x_center * image_width + (width * image_width) / 2
    y_max = y_center * image_height + (height * image_height) / 2
    
    # Ensure coordinates are within image boundaries
    x_min = max(0, int(x_min))
    y_min = max(0, int(y_min))
    x_max = min(image_width, int(x_max))
    y_max = min(image_height, int(y_max))
    
    # Crop the image
    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    
    return cropped_image

def most_frequent_class(data):
    classes = [mdata['class'] for mdata in data['metadatas'][0]]

    class_counter = Counter(classes)

    most_common_class, _ = class_counter.most_common(1)[0]
    
    return most_common_class

def classify(file:BytesIO, bboxes: list[Bbox]) -> list[BBoxResult]:
    results = []
    img = Image.open(file)
    
    for i in tqdm(range(len(bboxes))):
        bbx = bboxes[i]
        cur_img = crop_image(img, bbx.x, bbx.y, bbx.w, bbx.h)
        inputs = processor(text=["power bridge"], images=[cur_img], return_tensors="pt").to('cuda:0')
        with torch.no_grad():
            img_embeddgins = model(**inputs).image_embeds
            img_embeddgins = img_embeddgins / img_embeddgins.norm(p=2, dim=-1, keepdim=True)
        
        result = collection.query(
            query_embeddings=img_embeddgins.cpu().numpy(),
            n_results=TOP_K
        )
        # print(result)
        results.append(most_frequent_class(result))

    return results

if __name__ == "__main__":
    img_url = "https://hb.ru-msk.vkcloud-storage.ru/fits/towers.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=m3KNiQmw9Pfykv3nfBcHyx%2F20241201%2Fru-msk%2Fs3%2Faws4_request&X-Amz-Date=20241201T123155Z&X-Amz-Expires=2591999&X-Amz-SignedHeaders=host&X-Amz-Signature=f2c16d6f24c75e8581c7910a846abf205f7b2b2071d53f847edecff5729a7da8"
    response = requests.get(img_url)
    img_bytes = BytesIO(response.content)
    inputs = [
        Bbox(x=0.1902890625, y=0.3348229166666667, w=0.08817187500000001, h=0.38690624999999995),
        Bbox(x=0.5357109375, y=0.29464583333333333, w=0.13616406249999996, h=0.4047604166666666),
        Bbox(x=0.490515625, y=0.42634375, w=0.04129687499999992, h=0.12351041666666672)
    ]
    result = classify(img_bytes, inputs)
    print(result)