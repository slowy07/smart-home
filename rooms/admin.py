from django.contrib import admin
from .models import Device, DevicesTypes, Music

admin.site.register(
    Device,
    list_display = ["name", "room", "pin"]
)

admin.site.register(
    DevicesTypes,
    list_dsiplay = ["name", "iconclass", "style_type"]
)
admin.site.register(
    Music,
    list_display = ["name", "music"]
)