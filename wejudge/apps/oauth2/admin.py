from django.contrib import admin
import models
# Register your models here.
admin.site.register(models.Client)
admin.site.register(models.AuthCode)
admin.site.register(models.Tokens)
admin.site.register(models.UserAllowClient)