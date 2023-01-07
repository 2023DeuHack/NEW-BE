from rest_framework import serializers

from user.models import User
from user.serializers import UserSerializer

from .models import Diary, DiaryImage


class DiaryImageSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(use_url=True)

    class Meta:
        model = DiaryImage
        fields = ["image"]


class DiarySerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        image = obj.diaryimage_set.all()
        return DiaryImageSerializer(instance=image, many=True).data

    class Meta:
        model = Diary
        fields = ["id", "title", "content", "created_at", "images", "user"]

    def create(self, validated_data):
        instance = Diary.objects.create(**validated_data)
        image_set = self.context["request"].FILES
        for image_data in image_set.getlist("image"):
            DiaryImage.objects.create(diary=instance, image=image_data)
        return instance


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_image"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nickname"]


class DiaryListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()

    def get_images(self, obj):
        image = obj.diaryimage_set.all()
        return DiaryImageSerializer(instance=image, many=True).data

    def get_profile(self, obj):
        print(obj.user.profile_image)
        print(obj.diaryimage_set.all())
        return ProfileImageSerializer(instance=obj.user).data

    def get_like(self, obj):
        like = obj.like_users.all()
        return LikeSerializer(instance=like, many=True).data

    class Meta:
        model = Diary
        fields = ["id", "title", "created_at", "images", "user", "profile", "like"]
