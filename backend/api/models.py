from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    # Đặt USERNAME_FIELD thành 'email' nếu bạn muốn đăng nhập bằng email
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username'] # Nếu dùng email làm username, thì username vẫn là trường bắt buộc

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="api_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="api_user_permissions_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.email


class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    calories = models.IntegerField()
    def __str__(self): return f"{self.name} - {self.calories} kcal"

class MealHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_calories = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Bữa ăn của {self.user.username}"

class DetectedFood(models.Model):
    meal_history = models.ForeignKey(MealHistory, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    confidence = models.FloatField()
    def __str__(self): return self.food_item.name