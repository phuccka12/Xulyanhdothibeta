from django.urls import path
from .views import PredictAPIView
from .views import RegisterAPIView, LoginAPIView
urlpatterns = [
    path('predict/', PredictAPIView.as_view(), name='predict'),
    # Thêm các đường dẫn cho đăng ký và đăng nhập
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
]