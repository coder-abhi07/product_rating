from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import HarmfulIngredient

@admin.register(HarmfulIngredient)
class HarmfulIngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the 'name' field in the list view
