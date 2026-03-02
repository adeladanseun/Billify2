from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import exceptions

from .user_serializers import *
from .permissions import *

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def get_queryset(self, *args, **kwargs):
        return User.objects.all()

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if not settings.ALLOW_MULTIPLE_DEVICE_LOGIN:
                user_outstanding_token = OutstandingToken.objects.filter(user=user)
                for token in user_outstanding_token:
                    try:
                        RefreshToken(token.token).blacklist()
                    except exceptions.TokenError:
                         pass
            if user.is_active:
                refresh_token = RefreshToken.for_user(user)
                refresh_token.outstand()
                tokens = {"refresh": str(refresh_token),"access": str(refresh_token.access_token)}
                serializer = LoginSerializer(data=tokens)
                if serializer.is_valid():
                    return Response(serializer.data)
                else: return Response(serializer.errors, status=400)
            else: 
                return Response({
                    'status': 'User has been banned or is marked in_active'
                })

        return Response({'error': 'Invalid Credential'}, status=400)
            

class TestReturnAuth(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		if request.user.is_authenticated:
			return Response({
				"value": "user logged in"
			})
		return Response({
			"value": "Failed"
		})
	def post(self, request):
		return self.get(request)