from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import io
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer
from django.contrib.auth import get_user_model
from .apps import ApiConfig
from rest_framework.permissions import IsAuthenticated 
from .models import FoodItem, MealHistory, DetectedFood # Thêm import models
from rest_framework.authentication import TokenAuthentication # Thêm import này

User = get_user_model() 
# Lấy model User mà chúng ta đã định nghĩa
# View để đăng ký người dùng mới
class RegisterAPIView(APIView):
    permission_classes = [IsAuthenticated] # Thêm dòng này để yêu cầu xác thực
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Tạo một token cho user mới
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user_info': {
                    'username': user.username,
                    'email': user.email
                },
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Kế thừa từ view có sẵn của DRF để xử lý logic đăng nhập
class LoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })

# Database calo (tương tự như trước)
CALO_DATABASE = {
    'banh mi': 350, 'bun bo hue': 650, 'bun cha': 550, 'com tam': 650,
    'ga ran': 450, 'goi cuon': 200, 'khoai tay chien': 400, 'pho bo': 450
}

class PredictAPIView(APIView):
    permission_classes = [IsAuthenticated] # Yêu cầu user phải đăng nhập
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        if not file:
            return Response({'error': 'Không có file nào được gửi lên'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Lấy thông tin user đã được xác thực từ token
            current_user = request.user

            img = Image.open(file).convert("RGB")
            model = ApiConfig.model
            results = model.predict(img)

            predictions_list = []
            total_calories = 0

            # Tạo một bản ghi MealHistory mới cho lần upload này
            new_meal = MealHistory.objects.create(user=current_user, total_calories=0)

            for result in results:
                boxes = result.boxes.cpu().numpy()
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    
                    # Tìm món ăn trong DB, nếu chưa có thì tạo mới
                    # Điều này giúp bạn không cần hardcode CALO_DATABASE nữa
                    food_item, created = FoodItem.objects.get_or_create(
                        name=class_name,
                        defaults={'calories': 0} # Mặc định calo là 0 nếu chưa có
                    )
                    
                    calories = food_item.calories
                    total_calories += calories
                    
                    # Lưu món ăn được nhận diện vào DB, liên kết với bữa ăn
                    DetectedFood.objects.create(
                        meal_history=new_meal,
                        food_item=food_item,
                        confidence=float(box.conf[0])
                    )
                    
                    # Thêm vào danh sách để trả về cho frontend
                    predictions_list.append({
                        'class_name': class_name,
                        'confidence': float(box.conf[0]),
                        'calories': calories
                    })
            
            # Sau khi tính xong tổng calo, cập nhật lại cho bữa ăn
            new_meal.total_calories = total_calories
            new_meal.save()

            return Response({
                'detected_foods': predictions_list,
                'total_calories': total_calories
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
