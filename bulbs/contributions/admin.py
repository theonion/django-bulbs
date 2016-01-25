from django.contrib import admin

from .models import FreelanceProfile


class FreelanceProfileAdmin(admin.ModelAdmin):
    fields = ("payroll_name", "contributor", "is_freelance", "is_manager")


admin.site.register(FreelanceProfile, FreelanceProfileAdmin)
