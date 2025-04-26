from django.contrib import admin

# Register your models here.
from .models import LabelName, LabelLists

admin.site.register(LabelName)
admin.site.register(LabelLists)
