from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model

from recipe.models import Recipe, Ingredient, RecipeIngredient

User = get_user_model()
models = apps.get_models()

class RecipeAdmin(admin.ModelAdmin):
    list_display = ("author", "name", "text", "image")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("title", "dimension")


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)