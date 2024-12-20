from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipe_catalog.models import Recipe, Ingredient, RecipeIngredient
from datetime import timedelta
from decimal import Decimal

User = get_user_model()

class ContentTestCase(TestCase):
    RECIPE_URL = reverse('recipe_catalog:recipe_detail', args=[1])
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(username='contentuser', password='testpass')

        # Создаем базовые ингредиенты
        cls.flour = Ingredient.objects.create(
            name='Flour',
            weight=1000,
            weight_ready=900,
            price=Decimal('2.50')
        )
        cls.sugar = Ingredient.objects.create(
            name='Sugar',
            weight=500,
            weight_ready=500,
            price=Decimal('1.50')
        )
        cls.ingredients = [cls.flour, cls.sugar]
        
        # Создаем фиксированное количество рецептов
        cls.recipes = []
        for i in range(16):  # 16 рецептов для тестирования пагинации
            recipe = Recipe.objects.create(
                title=f'Recipe {i}',
                description=f'Description {i}',
                cooking_time=timedelta(minutes=30),
                author=cls.user
            )
            # Добавляем ингредиенты к рецепту
            recipe.ingredients.set(cls.ingredients)
            cls.recipes.append(recipe)
        
        # Создаем ингредиенты для тестового рецепта
        cls.flour = cls.ingredients[0]
        cls.water = cls.ingredients[1]

        # Создаем тестовый рецепт
        cls.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            cooking_time=timedelta(minutes=30),
            author=cls.user
        )
        # Добавляем ингредиенты к рецепту
        cls.recipe.ingredients.set(cls.ingredients)


    def test_ingredient_creation(self):
        """Test correct ingredient object creation"""
        self.assertEqual(self.flour.name, 'Flour')
        self.assertEqual(self.flour.weight, 1000)
        self.assertEqual(self.flour.weight_ready, 900)
        self.assertEqual(self.flour.price, Decimal('2.50'))

    def test_recipe_creation(self):
        """Test correct recipe object creation"""
        recipe = self.recipe
        self.assertTrue(recipe.ingredients.exists())
        self.assertEqual(recipe.cooking_time, timedelta(minutes=30))

    def test_ingredients_alphabetical_order(self):
        """Test ingredients are sorted alphabetically"""
        recipe = self.recipe
        recipe_ingredients = recipe.ingredients.order_by('name')
        self.assertEqual(list(recipe_ingredients), self.ingredients)
    
    # Test recipe view context -------------------------------------------------------------
    def test_recipes_list_view_context(self):
        """Test recipe list view context"""
        response = self.client.get(reverse('recipe_catalog:index'))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(len(context['recipes']), 10) # 10 recipes per page
        self.sorted_recipes = sorted(self.recipes, key=lambda recipe: recipe.title)
        for i, recipe in enumerate(context['recipes']):
            self.assertEqual(recipe.title, self.sorted_recipes[i].title)
            self.assertEqual(recipe.cooking_time, self.sorted_recipes[i].cooking_time)
            self.assertEqual(recipe.description, self.sorted_recipes[i].description)

    def test_recipe_view_context(self):
        """Test recipe detail view context"""
        url = reverse('recipe_catalog:recipe_detail', args=[self.recipes[0].id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['recipe_id'], self.recipes[0].id)
        self.assertEqual(context['title'], self.recipes[0].title)
        self.assertEqual(context['cooking_time'], self.recipes[0].cooking_time)
        self.assertEqual(context['description'], self.recipes[0].description)
        self.assertEqual(len(context['ingredients']), len(self.ingredients))
        for i, ingredient in enumerate(context['ingredients']):
            self.assertEqual(ingredient.name, self.ingredients[i].name)
    
    def test_recipe_ingredients_count(self):
        """Test recipe detail view context"""
        response = self.client.get(self.RECIPE_URL)
        context = response.context
        self.assertEqual(len(context['ingredients']), len(self.ingredients))

    def test_recipes_alphabetical_order(self):
        """Test recipes are sorted alphabetically on index page"""
        response = self.client.get(reverse('recipe_catalog:index'))
        recipes_in_context = response.context['recipes']
        
        sorted_titles = [recipe.title for recipe in recipes_in_context]
        self.assertEqual(sorted_titles, sorted(sorted_titles))

    def test_recipe_ingredient_relationship(self):
        """Test many-to-many relationship between recipes and ingredients"""
        recipe = self.recipe
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(self.flour, recipe.ingredients.all())
        self.assertIn(self.water, recipe.ingredients.all())
    

    def test_pagination_on_index_page(self):
        """Test that index page shows maximum 10 recipes per page"""
        response = self.client.get(reverse('recipe_catalog:index'))
        self.assertEqual(len(response.context['recipes']), 10)
        
        # Check second page
        response = self.client.get(f"{reverse('recipe_catalog:index')}?page=2")
        self.assertEqual(len(response.context['recipes']), 7)

    def test_recipe_ingredients_sorting(self):
        """Test ingredients are displayed in alphabetical order on recipe detail page"""
        recipe = Recipe.objects.first()
        url = reverse('recipe_catalog:recipe_detail', args=[recipe.id])
        response = self.client.get(url)
        
        ingredients = response.context['ingredients']
        ingredient_names = [i.name for i in ingredients]
        self.assertEqual(ingredient_names, sorted(ingredient_names))

    def test_recipe_form_visibility(self):
        """Test recipe form visibility based on authentication status"""
        create_url = reverse('recipe_catalog:recipe')
        # Анонимный пользователь
        response = self.client.get(create_url)
        self.assertRedirects(
            response,
            f'/auth/login/?next={create_url}',
            fetch_redirect_response=False
        )
        
        # Авторизованный пользователь
        self.client.force_login(self.user)
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        