from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CandidateProfile

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("HireFlow Role", {"fields": ("role",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("HireFlow Role", {"fields": ("role",)}),
    )


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "education")
    search_fields = ("user__username", "full_name", "user__email")
