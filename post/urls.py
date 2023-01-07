from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DiaryViewSet, FollowingViewSet, likes

diary_list = DiaryViewSet.as_view({"get": "list", "post": "create"})
diary_detail = DiaryViewSet.as_view({"get": "retrieve", "delete": "destroy"})

following_list = FollowingViewSet.as_view({"get": "list"})

urlpatterns = [
    path("diary/", diary_list, name="diary-list"),
    path("diary/<int:pk>/", diary_detail, name="diary-detail"),
    path("home/", following_list, name="following_list"),
    path("likes/<int:article_pk>", likes, name="likes"),
]
