from django.contrib import admin

from .models import Diary, DiaryImage

# Register your models here.

admin.site.register(Diary)

admin.site.register(DiaryImage)
