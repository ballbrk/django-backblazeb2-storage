from django.contrib import admin
from .models import *


class FileUploadAdmin( admin.ModelAdmin):
    list_display = ('file_id', 'name')
    save_as = True



admin.site.register(FileUpload,FileUploadAdmin)

