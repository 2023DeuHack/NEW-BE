import os
from uuid import uuid4

from django.db import models
from django.utils import timezone

from user.models import User


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


class Diary(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="diary_user", on_delete=models.CASCADE, null=True, to_field="nickname")
    like_users = models.ManyToManyField(User, related_name="like_articles")
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class DiaryImage(models.Model):
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_to_func, blank=True, null=True)
