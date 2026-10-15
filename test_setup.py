import torch
from qdrant_client import QdrantClient

def check_system():
    print("=== 1. ตรวจสอบการทำงานของ GPU (NVIDIA RTX) ===")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ กำลังใช้ CPU (หากต้องการความเร็วสูงควรตรวจสอบ PyTorch CUDA version)")

    print("\n=== 2. ตรวจสอบการเชื่อมต่อ Qdrant Database ===")
    try:
        client = QdrantClient(url="http://localhost:6333")
        collections = client.get_collections()
        print("เชื่อมต่อ Qdrant สำเร็จ!")
        print(f"Collections ปัจจุบัน: {collections.collections}")
    except Exception as e:
        print(f"❌ เชื่อมต่อ Qdrant ไม่สำเร็จ: {e}")

if __name__ == "__main__":
    check_system()