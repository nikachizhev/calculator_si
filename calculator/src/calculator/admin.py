from django.contrib import admin

from calculator.models import Calculation


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ("id", "client_id", "expression", "result", "created_at")
    list_filter = ("created_at",)
    search_fields = ("client_id", "expression", "result")
    readonly_fields = ("created_at",)

