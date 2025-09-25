from django.urls import path
from .views import RegisterAPIView, LoginAPIView, PredictAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('predict/', PredictAPIView.as_view(), name='predict'),
]