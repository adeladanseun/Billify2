from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Company


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CompanySerializer(serializers.ModelSerializer):
    currency = serializers.CharField(source='get_currency_display')
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'currency']

class LoginSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
