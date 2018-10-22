"""
admin.py
***********
Register models as below and they will show up on the admin page
"""
from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Element)
admin.site.register(Connection)
admin.site.register(EmbedLink)
admin.site.register(Activity)
admin.site.register(Outcome)
admin.site.register(ActivOut)
admin.site.register(UserAttributes)
