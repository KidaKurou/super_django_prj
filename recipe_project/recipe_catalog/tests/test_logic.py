from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe_catalog.models import Recipe, Ingredient, RecipeIngredient
from datetime import timedelta
from decimal import Decimal

User = get_user_model()

class TestRecipeCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', password='testpass')
        cls.user1 = User.objects.create_user(username='testuser1', password='testpass')
        cls.user2 = User.objects.create_user(username='testuser2', password='testpass')

        # Создаём тестовый ингредиент
        cls.ingredient = Ingredient.objects.create(
            name='Test Ingredient',
            weight=100,
            weight_ready=90,
            price=Decimal('5.00')
        )
        # Создаём тестовый рецепт
        cls.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            cooking_time=timedelta(minutes=30),
            author=cls.user1
        )
        # Связываем рецепт и ингредиент
        RecipeIngredient.objects.create(
            recipe=cls.recipe,
            ingredient=cls.ingredient
        )
        
        cls.delete_url = reverse('recipe_catalog:recipe_delete', args=[cls.recipe.id])
        cls.edit_url = reverse('recipe_catalog:recipe_edit', args=[cls.recipe.id])

    
    def test_anonymous_user_cannot_create_recipe(self):
        # Создаем тестовые данные на основе полей из модели Recipe
        form_data = {
            'title': 'Test Recipe',
            'description': 'Test Description',
            'cooking_time': '00:30:00',
            'ingredients': [self.ingredient.id]
        }
        # Совершаем запрос от анонимного клиента
        response = self.client.post(reverse('recipe_catalog:recipe'), data=form_data)
        # Проверяем редирект на страницу логина
        self.assertRedirects(
            response,
            '/auth/login/?next=/recipe/',
            fetch_redirect_response=False
        )
        # Проверяем, что рецепт не создался
        # self.assertEqual(Recipe.objects.count(), 1)  # Только тот, что в setUp
    
    def test_author_can_delete_recipe(self):
        # Авторизуем пользователя
        self.client.force_login(self.user1)
        # Отправляем POST запрос на удаление
        response = self.client.post(self.delete_url)
        # Проверяем редирект на список рецептов
        self.assertRedirects(response, reverse('recipe_catalog:index'))
        # Проверяем, что рецепт удалён
        self.assertEqual(Recipe.objects.count(), 0)
    
    def test_non_author_cannot_delete_recipe(self):
        # Создаём другого пользователя
        other_user = User.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        self.client.force_login(other_user)
        # Пытаемся удалить рецепт
        response = self.client.post(self.delete_url)
        # Проверяем, что получили ошибку доступа
        self.assertEqual(response.status_code, 403)  # PermissionDenied
        # Проверяем, что рецепт не был удалён
        self.assertTrue(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_author_can_edit_recipe(self):
        # Авторизуем автора рецепта
        self.client.force_login(self.user1)
        # Создаем данные для обновления
        form_data = {
            'title': 'Updated Recipe',
            'description': 'Updated Description',
            'cooking_time': '00:45:00',
            'ingredients': [self.ingredient.id]
        }
        # Отправляем POST запрос на редактирование
        response = self.client.post(self.edit_url, data=form_data)
        # Проверяем редирект на страницу рецепта
        self.assertRedirects(
            response, 
            reverse('recipe_catalog:recipe_detail', kwargs={'pk': self.recipe.pk})
        )
        # Обновляем объект из базы данных
        self.recipe.refresh_from_db()
        # Проверяем, что данные обновились
        self.assertEqual(self.recipe.title, 'Updated Recipe')
        self.assertEqual(self.recipe.description, 'Updated Description')
        self.assertEqual(self.recipe.cooking_time, timedelta(minutes=45))
    
    def test_non_author_cannot_edit_recipe(self):
        # Создаём и авторизуем другого пользователя
        other_user = User.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        self.client.force_login(other_user)
        # Пытаемся изменить рецепт
        form_data = {
            'title': 'Hacked Recipe',
            'description': 'Hacked Description',
            'cooking_time': '00:45:00',
            'ingredients': [self.ingredient.id]
        }
        response = self.client.post(self.edit_url, data=form_data)
        self.assertEqual(response.content.decode(), 'You can not edit this recipe')
        # Проверяем, что данные не изменились
        self.recipe.refresh_from_db()
        self.assertNotEqual(self.recipe.title, 'Hacked Recipe')

    def test_recipe_edit_permissions(self):
        """Test that only the author can edit their recipe"""
        edit_url = reverse('recipe_catalog:recipe_edit', args=[self.recipe.id])
        
        # Test unauthenticated user
        response = self.client.get(edit_url)
        expected_redirect = f'/auth/login/'
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False, target_status_code=200)
        
        # Test non-author user
        self.client.login(username='testuser2', password='testpass')
        response = self.client.get(edit_url)
        self.assertEqual(response.content.decode(), 'You can not edit this recipe')
        
        # Clear old auth
        self.client.logout()
        
        # Test author - используем force_login
        self.client.force_login(self.user1)  # user1 - это автор рецепта
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'recipe_catalog/recipe_form.html')

    def test_recipe_deletion(self):
        """Test recipe deletion permissions and functionality"""
        delete_url = reverse('recipe_catalog:recipe_delete', args=[self.recipe.id])
        
        # Test unauthenticated user
        response = self.client.post(delete_url)
        self.assertRedirects(
            response,
            f'/auth/login/?next={delete_url}',
            fetch_redirect_response=False
        )
        
        # Test non-author user
        self.client.login(username='testuser2', password='testpass')
        response = self.client.post(delete_url)
        # self.assertEqual(response.status_code, 403)  # PermissionDenied
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())
        
        # Clear old auth
        self.client.logout()
        
        # Test author
        self.client.force_login(self.user1)  # user1 - это автор рецепта
        response = self.client.post(delete_url)
        # self.assertRedirects(response, reverse('recipe_catalog:index'))
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_recipe_creation_auth_required(self):
        """Test that only authenticated users can create recipes"""
        create_url = reverse('recipe_catalog:recipe')
        recipe_data = {
            'title': 'New Recipe',
            'description': 'Test Description',
            'cooking_time': '00:45:00',
            'ingredients': [self.ingredient.id]
        }
        
        # Test unauthenticated user
        response = self.client.post(create_url, recipe_data)
        self.assertRedirects(
            response,
            f'/auth/login/?next={create_url}',
            fetch_redirect_response=False
        )
        
        # Test authenticated user
        self.client.login(username='testuser1', password='testpass')
        response = self.client.post(create_url, recipe_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify recipe was created
        new_recipe = Recipe.objects.filter(title='New Recipe').first()
        self.assertIsNotNone(new_recipe)
        self.assertEqual(new_recipe.description, 'Test Description')