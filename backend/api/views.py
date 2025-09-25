from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
from .apps import ApiConfig
from .serializers import UserRegisterSerializer
from .models import FoodItem, MealHistory, DetectedFood,User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .ai_model import model as ai_model
import traceback 
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(ObtainAuthToken):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})

# === View cho API Predict (SỬA LẠI HOÀN TOÀN) ===
class PredictAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        if not file:
            return Response({'error': 'Không có file nào được gửi lên'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Lấy user từ request (có thể không phải là instance đầy đủ)
            user_from_request = request.user

            # === ĐÂY LÀ PHẦN SỬA LỖI QUAN TRỌNG ===
            # Dùng ID của user đó để lấy lại một đối tượng User hoàn chỉnh từ DB
            try:
                current_user = User.objects.get(id=user_from_request.id)
            except User.DoesNotExist:
                return Response({'error': 'Không tìm thấy người dùng.'}, status=status.HTTP_404_NOT_FOUND)
            # =======================================

            img = Image.open(file).convert("RGB")
            model = ApiConfig.model # Hoặc ai_model nếu bạn dùng phương pháp mới
            results = model.predict(img)

            predictions_list = []
            total_calories = 0

            # Bây giờ, `current_user` chắc chắn là một instance hợp lệ
            new_meal = MealHistory.objects.create(user=current_user, total_calories=0)

            for result in results:
                boxes = result.boxes.cpu().numpy()
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    
                    food_item, created = FoodItem.objects.get_or_create(
                        name=class_name,
                        defaults={'calories': 0}
                    )
                    
                    calories = food_item.calories
                    total_calories += calories
                    
                    DetectedFood.objects.create(
                        meal_history=new_meal,
                        food_item=food_item,
                        confidence=float(box.conf[0])
                    )
                    
                    predictions_list.append({
                        'class_name': class_name,
                        'confidence': float(box.conf[0]),
                        'calories': calories
                    })
            
            new_meal.total_calories = total_calories
            new_meal.save()

            return Response({
                'detected_foods': predictions_list,
                'total_calories': total_calories
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(error_traceback)
            return Response({
                'error': 'Lỗi xử lý ở server.',
                'traceback': error_traceback
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)