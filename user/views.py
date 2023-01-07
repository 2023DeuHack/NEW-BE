from json.decoder import JSONDecodeError

import requests
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.http import JsonResponse
from django.shortcuts import redirect
from environ import Env
from rest_framework import filters, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer

env = Env()

state = "random_string"

BASE_URL = env("BASE_URL")
KAKAO_CALLBACK_URI = BASE_URL + "accounts/kakao/callback/"


def kakao_login(request):
    rest_api_key = env("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code")


def kakao_callback(request):
    rest_api_key = env("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI

    # code로 access token 요청
    token_req = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")

    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get("access_token")

    # access token으로 카카오톡 프로필 요청
    profile_request = requests.post("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})

    profile_json = profile_request.json()
    kakao_account = profile_json.get("kakao_account")
    print(kakao_account)
    email = kakao_account.get("email")

    # 이메일이 없으면 오류 => 카카오톡 최신 버전에서는 이메일 없이 가입 가능해서 추후 수정해야함
    if email is None:
        return JsonResponse({"err_msg": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)

        social_user = SocialAccount.objects.get(user=user)

        if social_user is None:
            return JsonResponse({"err_msg": "email exists but not social user"}, status=status.HTTP_400_BAD_REQUEST)

        if social_user.provider != "kakao":
            return JsonResponse({"err_msg": "no matching social type"}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 kakao로 회원가입된 유저면 로그인 & 해당 유저의 jwt 발급
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)

        accept_json = accept.json()
        print(accept_json)
        accept_json.pop("user", None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}

        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)

    except SocialAccount.DoesNotExist:
        return JsonResponse({"err_msg": "email exists but not social user"}, status=status.HTTP_400_BAD_REQUEST)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]  # 👈 DjangoFilterBackend 지정
    search_fields = ["^nickname"]  # 👈 filtering 기능을 사용할 field 입력


class MyFollowView(APIView):
    def get(self, request):
        try:
            me = request.user

            data = dict()
            data["following"] = list(map(lambda x: x.nickname, request.user.followers.all()))
            data["followers"] = list(map(lambda x: x.nickname, User.objects.filter(followers=me)))

            return JsonResponse(data)
        except User.DoesNotExist:
            return JsonResponse({"err_msg": "Nickname does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        data = dict(zip(request.data.keys(), request.data.values()))

        if "nickname" not in data:
            return JsonResponse({"err_msg": "Nickname does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        you: User = User.objects.get(nickname=data["nickname"])
        me: User = request.user

        if you in me.followers.all():
            me.followers.remove(you)
            return Response("unfollow", status=status.HTTP_200_OK)
        else:
            me.followers.add(you)
            return Response("follow", status=status.HTTP_200_OK)


class FollowView(APIView):
    def get(self, request, nickname):
        try:
            me = request.user

            data = dict()
            data["following"] = list(map(lambda x: x.nickname, User.objects.get(nickname=nickname).followers.all()))
            data["followers"] = list(map(lambda x: x.nickname, User.objects.filter(followers=me)))

            return JsonResponse(data)
        except User.DoesNotExist:
            return JsonResponse({"err_msg": "Nickname does not exist."}, status=status.HTTP_400_BAD_REQUEST)
