from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'account', 'password', 'role', 'created_time', 'is_active')
        extra_kwargs = {
            'password': {'write_only': True},
            'created_time': {'read_only': True},
            'is_active': {'read_only': True}
        }

    def create(self, validated_data):
        # 确保正确创建用户并加密密码
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # 使用set_password而不是直接赋值
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance 