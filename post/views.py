from django.db.models import Count, F, Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from user.models import User

from .models import Diary
from .serializers import DiaryListSerializer, DiarySerializer

# class PostViewSet(ModelViewSet):
#     queryset = Diary.objects.all().order_by("-created_at")
#     serializer_class = DiarySerializer


class DiaryViewSet(ModelViewSet):

    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DiarySerializer

    def get_queryset(self):
        return self.request.user.diary_user.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.request.user.diary_user.all()
        serializer = DiaryListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingViewSet(ModelViewSet):

    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = DiarySerializer

    def get_queryset(self):
        return Diary.objects.filter(user__in=self.request.user.followers.all())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = Diary.objects.filter(user__in=self.request.user.followers.all())
        print(self.request.user.followers.all())
        serializer = DiaryListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def likes(request, article_pk):
    if request.method == "GET":
        article = get_object_or_404(Diary, id=article_pk)

        if article.like_users.filter(nickname=request.user.nickname).exists():
            article.like_users.remove(request.user)
            return Response("unlike", status=status.HTTP_200_OK)
        else:
            article.like_users.add(request.user)
            return Response("like", status=status.HTTP_200_OK)
