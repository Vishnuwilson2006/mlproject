from django.contrib import admin
from .models import PredictionHistory

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'circuit_title', 'circuit_category', 'user', 'performance_score', 'created_at')
    list_filter = ('created_at', 'circuit_category', 'user')
    search_fields = ('id', 'circuit_title', 'circuit_slug', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
