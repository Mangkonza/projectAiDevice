import io
import os
import urllib.parse
import torch
import torch.nn.functional as F
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from transformers import AutoImageProcessor, AutoModel
from qdrant_client import QdrantClient

app = FastAPI(title="IT Device Visual Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
possible_paths = [
    os.path.join(PROJECT_ROOT, "Documents", "keyboard"),
    os.path.join(CURRENT_DIR, "Documents", "keyboard"),
    os.path.abspath("Documents/keyboard"),
]
PRODUCTS_FOLDER = next((p for p in possible_paths if os.path.exists(p)), possible_paths[0])

if os.path.exists(PRODUCTS_FOLDER):
    print(f"✅ กำลังเสิร์ฟภาพสินค้าจาก: {PRODUCTS_FOLDER}")
    app.mount("/static/products", StaticFiles(directory=PRODUCTS_FOLDER), name="products")

COLLECTION_NAME = "it_devices"
QDRANT_URL = "http://localhost:6333"
MODEL_NAME = "facebook/dinov2-base"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"กำลังโหลดโมเดล {MODEL_NAME} บน {device}...")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

client = QdrantClient(url=QDRANT_URL)
print("🚀 Backend (DINOv2 Base) พร้อมให้บริการแล้ว!")

def clean_display_name(filename: str):
    name = os.path.splitext(filename)[0]
    name = name.replace("KEYBOARD--คีย์บอร์ด--", "").replace("MOUSE--เมาส์--", "")
    return name.replace("---", " - ").replace("--", " ").replace("-", " ").strip()

def extract_query_vector(image: Image.Image):
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        vector = outputs.last_hidden_state[:, 0, :]
        normalized_vector = F.normalize(vector, p=2, dim=-1)
    return normalized_vector.squeeze().cpu().tolist()

@app.post("/api/search")
async def search_device(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    query_vector = extract_query_vector(image)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    ).points

    matches = []
    for hit in results:
        payload = hit.payload or {}
        raw_filename = payload.get("filename", "")
        encoded_filename = urllib.parse.quote(raw_filename) if raw_filename else ""

        matches.append({
            "score": round(hit.score * 100, 2),
            "display_name": payload.get("display_name") or clean_display_name(raw_filename),
            "filename": raw_filename,
            "image_url": f"http://127.0.0.1:8000/static/products/{encoded_filename}" if raw_filename else None,
            "category": payload.get("category", "อุปกรณ์ไอที"),
        })

    return {"status": "success", "matches": matches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)