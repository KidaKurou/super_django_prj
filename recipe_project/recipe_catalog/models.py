from django.db import models
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    weight = models.PositiveIntegerField()
    weight_ready = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='recipe_images/', blank=True, null=True)
    cooking_time = models.DurationField(default=timedelta(minutes=5))
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ingredient} - {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        ]
        indexes = [
            models.Index(fields=['recipe', 'ingredient'])
        ]
