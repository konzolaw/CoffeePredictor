from django.contrib import admin # type: ignore
from .models import FarmInfo, coffee, YieldPrediction

admin.site.register(coffee)

@admin.register(FarmInfo)
class FarmInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'farmer_id', 'coffee_variety', 'fertilizer_amount', 'hectares_of_land', 'previous_yield', 'presence_of_buds', 'weather_condition', 'submitted_at')
    search_fields = ('user__username', 'farmer_id', 'coffee_variety')
    list_filter = ('presence_of_buds', 'fertilizer_amount', 'user', 'coffee_variety')

@admin.register(YieldPrediction)
class YieldPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_yield', 'confidence_level', 'created_at')
    search_fields = ('user__username', 'predicted_yield')
    list_filter = ('confidence_level', 'user')