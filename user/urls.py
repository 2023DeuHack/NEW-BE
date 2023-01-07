from django.urls import include, path, re_path
from rest_framework import routers

from .views import (
    FollowView,
    KakaoLogin,
    MyFollowView,
    StudentViewSet,
    kakao_callback,
    kakao_login,
)

router = routers.DefaultRouter()
router.register("", StudentViewSet)

urlpatterns = [
    path("search/", include(router.urls)),
    # 카카오 소셜 로그인
    path("kakao/login/", kakao_login, name="kakao_login"),
    path("kakao/callback/", kakao_callback, name="kakao_callback"),
    path("kakao/login/finish/", KakaoLogin.as_view(), name="kakao_login_todjango"),
    # 팔로우
    path("follow/", MyFollowView.as_view()),
    path("follow/<str:nickname>/", FollowView.as_view()),
]
