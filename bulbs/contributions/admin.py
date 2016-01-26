from django.contrib import admin

from .models import FreelanceProfile


class FreelanceProfileAdmin(admin.ModelAdmin):
    fields = ("payroll_name", "is_freelance", "is_manager")
    list_display = ("get_full_name",)

    def get_queryset(self, request):
        qs = super(FreelanceProfileAdmin, self).get_queryset(request)
        return qs.distinct()

    def get_full_name(self, obj):
        return obj.contributor.get_full_name()
    get_full_name.admin_order_field = 'contributor'


admin.site.register(FreelanceProfile, FreelanceProfileAdmin)
