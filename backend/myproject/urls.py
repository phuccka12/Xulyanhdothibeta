from django.contrib import admin
from django.urls import path, include # Thêm include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # Thêm dòng này
]