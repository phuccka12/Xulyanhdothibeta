from django.apps import AppConfig
from ultralytics import YOLO
import sys

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
try:
        model = YOLO('best.pt')
        print("✅ Django App: Model AI best.pt đã được tải thành công!")
        # Gán model vào class để các nơi khác có thể truy cập
        AppConfig.model = model
except Exception as e:
        print(f"❌ Django App: Lỗi khi tải model AI: {e}")
        sys.exit()