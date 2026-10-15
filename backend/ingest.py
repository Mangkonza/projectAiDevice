import os
import uuid
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import AutoImageProcessor, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

COLLECTION_NAME = "it_devices"
QDRANT_URL = "http://localhost:6333"
MODEL_NAME = "facebook/dinov2-base"
VECTOR_SIZE = 768

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
possible_paths = [
    os.path.join(PROJECT_ROOT, "Documents", "keyboard"),
    os.path.join(CURRENT_DIR, "Documents", "keyboard"),
    os.path.abspath("Documents/keyboard"),
]
PRODUCTS_DIR = next((p for p in possible_paths if os.path.exists(p)), possible_paths[0])

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"กำลังใช้งาน Device: {device}")

print(f"กำลังโหลดโมเดล {MODEL_NAME}...")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

def extract_vector(image_path: str):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        vector = outputs.last_hidden_state[:, 0, :]
        normalized_vector = F.normalize(vector, p=2, dim=-1)
    return normalized_vector.squeeze().cpu().tolist()

def parse_filename(filename: str):
    base_name = os.path.splitext(filename)[0]
    clean_name = base_name.replace("KEYBOARD--คีย์บอร์ด--", "").replace("MOUSE--เมาส์--", "")
    return {
        "display_name": clean_name.replace("---", " - ").replace("--", " ").replace("-", " ").strip(),
        "filename": filename,
        "category": "keyboard" if "KEYBOARD" in base_name else "mouse",
    }

def main():
    client = QdrantClient(url=QDRANT_URL)

    print(f"สร้าง Collection: {COLLECTION_NAME} (ขนาด {VECTOR_SIZE} มิติ)")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    image_files = [f for f in os.listdir(PRODUCTS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    print(f"พบรูปภาพสินค้า {len(image_files)} รูป กำลังนำเข้า...")

    points = []
    for filename in image_files:
        filepath = os.path.join(PRODUCTS_DIR, filename)
        try:
            vector = extract_vector(filepath)
            payload = parse_filename(filename)
            payload["image_path"] = filepath
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, filename))
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))
        except Exception as e:
            print(f"Error {filename}: {e}")

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"\n✅ บันทึกข้อมูลเข้าสู่ Qdrant (DINOv2-Base) สำเร็จ!")

if __name__ == "__main__":
    main()