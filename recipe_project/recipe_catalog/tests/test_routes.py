from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus
from recipe_catalog.models import Recipe, Ingredient, RecipeIngredient
from datetime import timedelta

User = get_user_model()

class RouteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.client = Client()
        
        # Create test ingredient
        cls.ingredient = Ingredient.objects.create(
            name='Test Ingredient', 
            weight=100, 
            weight_ready=80, 
            price=10.50
        )
        
        # Create test recipe
        cls.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            cooking_time=timedelta(minutes=30)
        )
        
        # Link ingredient to recipe
        RecipeIngredient.objects.create(
            recipe=cls.recipe, 
            ingredient=cls.ingredient
        )

    def test_index_route(self):
        """Test index page route accessibility"""
        response = self.client.get(reverse('recipe_catalog:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe_catalog/index.html')

    def test_about_route(self):
        """Test about page route accessibility"""
        response = self.client.get(reverse('recipe_catalog:about'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe_catalog/about.html')

    def test_recipe_detail_route(self):
        """Test specific recipe detail page route"""
        response = self.client.get(reverse('recipe_catalog:recipe_detail', kwargs={'pk': self.recipe.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe_catalog/recipe.html')

    def test_nonexistent_recipe_route(self):
        """Test route for non-existent recipe"""
        non_existent_id = Recipe.objects.count() + 999
        response = self.client.get(reverse('recipe_catalog:recipe_detail', kwargs={'pk': non_existent_id}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    
    def test_ingredient_routes(self):
        """Test ingredient-related routes"""
        # Test ingredients list (public access)
        response = self.client.get(reverse('recipe_catalog:ingredients'))
        self.assertEqual(response.status_code, 200)
        
        # Test ingredient creation (requires auth)
        create_url = reverse('recipe_catalog:ingredient')
        
        # Test unauthenticated
        response = self.client.get(create_url)
        self.assertRedirects(
            response,
            f'/auth/login/?next={create_url}',
            fetch_redirect_response=False
        )
        
        # Test authenticated
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)

    def test_auth_routes(self):
        """Test authentication-related routes"""
        login_url = '/auth/login/'
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)