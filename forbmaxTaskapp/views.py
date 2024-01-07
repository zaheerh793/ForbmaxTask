import json
from rest_framework.views import APIView
from django.db import models
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import GroupSerializer
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer, ContentSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Content, Group
from rest_framework import generics


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            print("zaheer hussain")
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        user_ids = data.get('users', '[]')
        user_ids = json.loads(user_ids)
        data['creation_name'] = request.user.username
        serializer = GroupSerializer(data=data)
        if serializer.is_valid():
            group = serializer.save()
            group.users.add(request.user)
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    group.users.add(user)
                except User.DoesNotExist:
                    return Response({'error': f'User with ID {user_id} does not exist.'},
                                    status=status.HTTP_400_BAD_REQUEST)
            group.save()
            return Response({'message': 'Group created successfully!'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentCreateView(generics.CreateAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().post(request, *args, **kwargs)


class ContentView(generics.ListAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(Group.objects.all())
        groups = Group.objects.filter(users=user.id).all()
        return Content.objects.filter(
            models.Q(visibility='public') | models.Q(user=user) | models.Q(tag_group__in=groups)
        )
