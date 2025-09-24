from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import io

# Import AppConfig để truy cập model đã tải
from .apps import ApiConfig

# Database calo (tương tự như trước)
CALO_DATABASE = {
    'banh mi': 350, 'bun bo hue': 650, 'bun cha': 550, 'com tam': 650,
    'ga ran': 450, 'goi cuon': 200, 'khoai tay chien': 400, 'pho bo': 450
}

class PredictAPIView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        if not file:
            return Response({'error': 'Không có file nào được gửi lên'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            img = Image.open(file).convert("RGB")
            # Lấy model từ AppConfig
            model = ApiConfig.model
            results = model.predict(img)

            predictions_json = []
            total_calories = 0
            for result in results:
                boxes = result.boxes.cpu().numpy()
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    calories = CALO_DATABASE.get(class_name, 0)
                    total_calories += calories
                    predictions_json.append({
                        'class_name': class_name,
                        'confidence': float(box.conf[0]),
                        'calories': calories,
                        'box_coordinates': [float(coord) for coord in box.xyxy[0]]
                    })

            return Response({
                'detected_foods': predictions_json,
                'total_calories': total_calories
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)