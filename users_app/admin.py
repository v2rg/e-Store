from django.contrib import admin

# Register your models here.

from users_app.models import User, UserAddress, EmailVerification

admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(EmailVerification)
