import os
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel
from qdrant_client import QdrantClient

# 1. ตั้งค่าพื้นฐาน
COLLECTION_NAME = "it_devices"
QDRANT_URL = "http://localhost:6333"

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"กำลังใช้งาน Device สำหรับค้นหา: {device}")

# 2. โหลดโมเดลตัวเดียวกับตอน Ingest
print("กำลังโหลดโมเดล DINOv2...")
processor = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
model = AutoModel.from_pretrained("facebook/dinov2-base").to(device)
model.eval()

# 3. ฟังก์ชันแปลงภาพทดสอบเป็น Vector
def extract_vector(image_path: str):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        vector = outputs.last_hidden_state[:, 0, :].squeeze().cpu().tolist()
    return vector

# 4. ฟังก์ชันค้นหาใน Qdrant
def search_device(image_path: str, top_k: int = 3):
    if not os.path.exists(image_path):
        print(f"❌ ไม่พบไฟล์รูปภาพทดสอบ: {image_path}")
        return

    print(f"\n🔍 กำลังวิเคราะห์รูปภาพ: {image_path}")
    query_vector = extract_vector(image_path)

    client = QdrantClient(url=QDRANT_URL)
    
    # ค้นหาเวกเตอร์ที่ใกล้เคียงที่สุด
    search_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points

    print("\n" + "="*50)
    print("🎯 ผลลัพธ์การค้นหาอุปกรณ์ที่ใกล้เคียงที่สุด:")
    print("="*50)

    for rank, hit in enumerate(search_results, start=1):
        score = hit.score
        payload = hit.payload
        similarity_percent = score * 100

        print(f"\nอันดับที่ {rank}: ความคล้ายคลึง {similarity_percent:.2f}% (Score: {score:.4f})")
        print(f"  - ไฟล์ต้นฉบับ: {payload.get('filename')}")
        print(f"  - ประเภท: {payload.get('category')}")
        print(f"  - แบรนด์: {payload.get('brand')}")
        print(f"  - รุ่น: {payload.get('model_name')}")

if __name__ == "__main__":
    # ระบุ Path รูปที่ต้องการนำมาทดสอบค้นหา
    TEST_IMAGE_PATH = "Documents/test/test_1.jpg"
    search_device(TEST_IMAGE_PATH, top_k=3)