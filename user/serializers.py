from dj_rest_auth.serializers import UserDetailsSerializer
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import exceptions, serializers

from .models import User

UserModel = get_user_model()


class UserDetailsSerializer(UserDetailsSerializer):
    class Meta:
        model = UserModel
        extra_fields = []

        if hasattr(UserModel, "USERNAME_FIELD"):
            extra_fields.append(UserModel.USERNAME_FIELD)

        extra_fields.append("username")
        extra_fields.append("nickname")
        extra_fields.append("profile_image")
        extra_fields.append("introduce")

        fields = ("pk", *extra_fields)
        read_only_fields = ("email",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["followers"]


class followSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["followers"]


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(
        required=False,
        max_length=100,
    )
    nickname = serializers.CharField(
        required=False,
        max_length=100,
    )

    def validate_username(self, username):
        return username

    def validate_nickname(self, nickname):
        if User.objects.filter(nickname=nickname).exists():
            raise exceptions.ValidationError('Nickname "%s" is already in use.' % nickname)
        return nickname

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        print(self.validated_data)
        data_dict["nickname"] = self.validated_data.get("nickname", "")
        return data_dict


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={"input_type": "password"})

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = 'Must include "email" and "password".'
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = None

        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = "User account is disabled."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Unable to log in with provided credentials."
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if "rest_auth.registration" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(("E-mail is not verified."))

        attrs["user"] = user
        return attrs
