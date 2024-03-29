from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=300)
    dimension = models.CharField(max_length=300)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=10)
    slug = models.SlugField(unique=True, max_length=100)
    color = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=300)
    image = models.ImageField(upload_to='recipes/', )
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         through_fields=('recipe',
                                                         'ingredient'))
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    amount = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return (f'{self.ingredient.title} - {self.amount} '
                f'({self.ingredient.dimension})')


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ('user', 'author')


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='user')
    favorite_recipe = models.ForeignKey(Recipe,
                                        on_delete=models.CASCADE,
                                        related_name='favorite_recipe')

    class Meta:
        ordering = ['-id']


class ShoppingList(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='purchases_user')
    purchase_recipe = models.ForeignKey(Recipe,
                                        on_delete=models.CASCADE,
                                        related_name='purchases')
