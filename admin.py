from django.contrib import admin
from .models import Student, Grade, Subject  # Change 'Subjects' to 'Subject'
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(Grade)
admin.site.register(Subject)  # Register the Subject model
