from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient

# Register your models here.
class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 5

class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = ('title', 'description')


admin.site.register(Recipe, RecipeAdmin)

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'weight_ready', 'price')


admin.site.register(Ingredient, IngredientAdmin)
