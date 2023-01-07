import os
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


def upload_to_func(instance, filename):
    prefix = timezone.now().strftime("%Y/%m/%d")
    file_name = uuid4().hex
    extension = os.path.splitext(filename)[-1].lower()  # 확장자 추출
    return "/".join(
        [
            prefix,
            file_name + extension,
        ]
    )


class UserManager(BaseUserManager):
    def create_user(self, email, username, nickname, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, nickname, password):
        user = self.create_user(
            email,
            username=username,
            nickname=nickname,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=100, unique=False, null=False, blank=False)
    nickname = models.CharField(max_length=100, unique=True, blank=True, null=True, default=None)

    profile_image = models.ImageField(upload_to=upload_to_func, blank=True)
    introduce = models.CharField(max_length=100, blank=True)
    followers = models.ManyToManyField("self", symmetrical=False, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nickname"]

    def __str__(self):
        return f"email: {self.email}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
