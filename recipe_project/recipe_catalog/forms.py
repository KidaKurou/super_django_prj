from django import forms

from recipe_catalog.models import Ingredient, Recipe

class UserForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100, required=False)
    email = forms.EmailField(label='Email', required=False)

class IngredientForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'weight', 'weight_ready', 'price',)
        labels = {
            'name': 'Name',
            'weight': 'Weight',
            'weight_ready': 'Weight ready',
            'price': 'Price'
        }
        help_texts = {
            'name': 'Enter the name of the ingredient',
            'weight': 'Enter the weight of the ingredient in grams',
            'weight_ready': 'Enter the weight of the ingredient in grams after cooking',
            'price': 'Enter the price of the ingredient in rubles'
        }
        model = Ingredient

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ('author',)
        fields = ('title', 'description', 'cooking_time', 'image', 'ingredients')
        labels = {
            'title': 'Title',
            'description': 'Description',
            'cooking_time': 'Cooking time',
            'image': 'Image',
            'ingredients': 'Ingredients'
        }
        help_texts = {
            'title': 'Enter the title of the recipe',
            'description': 'Enter the description of the recipe',
            'cooking_time': 'Enter the cooking time of the recipe in minutes',
            'image': 'Upload an image for the recipe',
            'ingredients': 'Select the ingredients for the recipe'
        }
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'ingredients': forms.SelectMultiple(attrs={'class': 'select2'}),
        }