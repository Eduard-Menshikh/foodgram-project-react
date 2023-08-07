from django.contrib import admin

from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient, User


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass