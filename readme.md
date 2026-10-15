เปิด terminal เข้าไปที่โปรเจค แล้วรัน docker compose up -d

แล้วเปิด docker รันคอนเทนเนอร์ชื่อ qdrant มันจะเปิดพอร์ต http://localhost:6333/dashboard#/collections

แล้วเปิดไฟล์โปรเจค 
1.python -m venv venv
.\venv\Scripts\activate
2.pip install fastapi uvicorn qdrant-client torch torchvision transformers

รันครั้งแรกเพื่อเอาไฟล์ภาพใน Documents/keyboard แปลงเป็น ข้อมูลเก็บเข้าดาต้าเบส
python backend/ingest.py


รันโปรเจคหลังบ้าน
python backend/app.py

เปิดอีกterminal เพื่อรันโปรเจคหน้าบ้าน
cd frontend
npm install
npm run dev

เข้าใช้งานได้ที่ http://localhost:5173/
