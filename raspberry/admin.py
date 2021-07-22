from django.contrib import admin
from .models import GPIO_pins

admin.site.register(GPIO_pins, list_display=["pin", "gpio_state", "default_state"])
