# Nội dung file: backend/api/ai_model.py

from ultralytics import YOLO
import sys

try:
    # Tải model và lưu vào biến `model`
    model = YOLO('best.pt')
    print("✅ AI Model: Model đã được tải thành công!")
except Exception as e:
    # Nếu có lỗi, in ra và thoát
    print(f"❌ AI Model: Lỗi nghiêm trọng khi tải model - {e}")
    model = None
    sys.exit()