from django.db import models
from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,)

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug тэга',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                0,
                message='Время приготовления должно быть больше 0'
            ),
            MaxValueValidator(
                1000,
                message='Время приготовления должно быть меньше 1000'
            )
        ],
        verbose_name='Время приготовления в минутах',
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients',
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                0,
                message='Количество ингредиента должно быть больше 0.'
            ),
            MaxValueValidator(
                20000,
                message='Количество ингредиента должно быть меньше 20000.'
            )
        ],
        verbose_name='Количество',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_combination',
            )
        ]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def _str__(self):
        return f'{self.ingredient} - {self.amount}'


class AbstractFavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique_user_recipe'
            )
        ]
        default_related_name = '%(class)s_recipe'

    def __str__(self):
        return f'{self.user} - {self.recipe} [{self._meta.verbose_name}]'


class Favorite(AbstractFavoriteShoppingCart):
    class Meta(AbstractFavoriteShoppingCart.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(AbstractFavoriteShoppingCart):
    class Meta(AbstractFavoriteShoppingCart.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
