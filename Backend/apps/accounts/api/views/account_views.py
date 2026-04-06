from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.api.serializers.account_serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer
)
from apps.b2b.models import ColdStorage

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user   = serializer.save()
        # 🔥 Auto-create ColdStorage
        if user.role == user.Role.COLD_STORAGE:
            ColdStorage.objects.get_or_create(
                owner=user,
                defaults={
                    "name": f"{user.phone} Storage",
                    "address": ""
                }
            )
        tokens = get_tokens_for_user(user)
        return Response({
            "user":   UserSerializer(user).data,
            "tokens": tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user   = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        return Response({
            "user":   UserSerializer(user).data,
            "tokens": tokens,
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)