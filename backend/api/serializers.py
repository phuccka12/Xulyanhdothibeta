from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model() # Lấy model User mà chúng ta đã định nghĩa

# Serializer cho việc đăng ký
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        # Kiểm tra xem hai mật khẩu có khớp nhau không
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Mật khẩu không khớp.")
        # Kiểm tra độ dài tối thiểu của mật khẩu
        if len(data['password']) < 8:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        return data

    def create(self, validated_data):
        # Tạo người dùng mới với mật khẩu đã được mã hóa
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user