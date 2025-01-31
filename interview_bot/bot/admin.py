from django.contrib import admin
from .models import *  # Import your models here

# Register your models here.
admin.site.register(posts)
admin.site.register(conversation)
admin.site.register(questions)
admin.site.register(summary)
