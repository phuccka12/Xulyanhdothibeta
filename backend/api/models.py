from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission # Dòng import đã được sửa đúng
from datetime import datetime

# Bảng 1: User (Người dùng)
class User(AbstractUser):
    email = models.EmailField(unique=True)

    # Thêm các trường này để giải quyết xung đột với model User mặc định của Django
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="api_user_set", # Tên mới để tránh xung đột
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="api_user_permissions_set", # Tên mới để tránh xung đột
        related_query_name="user",
    )

# Bảng 2: FoodItem (Danh sách Món ăn)
class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    calories = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.calories} kcal"

# Bảng 3: MealHistory (Lịch sử Bữa ăn)
class MealHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    total_calories = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bữa ăn của {self.user.username} lúc {self.created_at.strftime('%Y-%m-%d %H:%M')}"

# Bảng 4: DetectedFood (Món ăn được Nhận diện)
class DetectedFood(models.Model):
    meal_history = models.ForeignKey(MealHistory, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    confidence = models.FloatField()

    def __str__(self):
        return f"{self.food_item.name} trong bữa ăn #{self.meal_history.id}"
    