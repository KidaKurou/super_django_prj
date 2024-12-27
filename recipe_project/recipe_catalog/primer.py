from recipe_project.recipe_catalog.models import Ingredient, Recipe, RecipeIngredient
from recipe_project.recipe_project import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import timedelta
from http import HTTPStatus

User = get_user_model()

# Create your tests here.
class TestOne(TestCase):
    def test_always_pass(self):
        """Always pass"""
        self.assertTrue(True)

class TestTwo(TestCase):
    def test_always_fail(self):
        """Always fail"""
        self.assertTrue(False)

class TestOneTemplate(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class TestOneDB(TestCase):
    RECIPE_TITLE = "Яичница"
    INGREDIENT_NAME = "Яйцо"

    @classmethod
    def setUpTestData(cls):
        cls.ingredient_egg = Ingredient.objects.create(
            name=cls.INGREDIENT_NAME, weight=10, weight_ready=10, price=10
        )
        cls.recipe = Recipe.objects.create(
            title=cls.RECIPE_TITLE,
            description="Яичница",
            cooking_time=timedelta(minutes=10),
            image="Egg",
            ingredients=[cls.ingredient_egg]
        )
        cls.recipe.ingredients.set([cls.ingredient_egg])

    def test_successful_creation_ingredient(self):
        ingredient_count = Ingredient.objects.count()
        self.assertEqual(ingredient_count, 1)

    def test_successful_creation_recipe(self):
        recipe_count = Recipe.objects.count()
        self.assertEqual(recipe_count, 1)

    def test_successful_creation_recipe_ingredient(self):
        counts = [
            (self.recipe.ingredients.count(), 1, "Рецепт"),
            (RecipeIngredient.objects.count(), 1, "Ингредиент-Рецепт")
        ]
        for cnt in counts:
            with self.subTest(msg='Рецепты-ингредиенты'):
                self.assertEqual(cnt[0], cnt[1], cnt[2])

    def test_titles(self):
        titles = [
            (self.ingredient_egg.name, self.INGREDIENT_NAME, 'Ингредиент'),
            (self.recipe.title, self.RECIPE_TITLE, 'Рецепт')
        ]
        for name in titles:
            with self.subTest(msg=f'Название {name[2]}'):
                self.assertEqual(name[0], name[1])


class TestCatalog(TestCase):
    INDEX_URL = reverse('recipe_catalog:index')
    RECIPE_TITLE = "Яичница"

    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.user = User.objects.create_user(username='testuser')
        # Create a client
        cls.client = Client()
        # Login
        cls.client.force_login(cls.user)
        # Create test recipe
        cls.recipe = Recipe.objects.create(
            title=cls.RECIPE_TITLE,
            description="Яичница",
            cooking_time=timedelta(minutes=10),
            image="Egg"
        )

    def test_home_page1(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_page2(self):
        url = reverse('recipe_catalog:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_ok(self):
        url = reverse('recipe_catalog:recipe_detail', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

class TestCatalog2(TestCase):
    INDEX_URL = reverse('recipe_catalog:index')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.client = Client()
        cls.client.force_login(cls.user)
        all_recipes = []
        for index in range(settings.OBJS_ON_PAGE + 1):
            news = Recipe(
                title=f'{index}',
                description=f'{index}',
                cooking_time=timedelta(minutes=10),
                image="Egg"
            )
            all_recipes.append(news)
        Recipe.objects.bulk_create(all_recipes)  # создаем несколько рецептов

    def test_index_count_recipes(self):
        response = self.client.get(self.INDEX_URL)
        object_list = response.context['recipes']
        news_count = object_list.count()
        self.assertEqual(news_count, settings.OBJS_ON_PAGE)
