from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from .forms import IngredientForm, RecipeForm, UserForm
from .models import Ingredient, Recipe


# Главная страница, Вывод списка рецептов
def index(request):
    recipes_list = Recipe.objects.order_by('title')
    paginator = Paginator(recipes_list, 10)
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)
    return render(request, 'recipe_catalog/index.html', {'recipes': recipes})


def about(request):
    return render(request, 'recipe_catalog/about.html')


def recipe_detail(request, pk):
    try:
        recipe = Recipe.objects.get(pk=pk)
    except Recipe.DoesNotExist:
        return handle_error_404(request)
    context = {
        'recipe_id': recipe.id,
        'title': recipe.title,
        'cooking_time': recipe.cooking_time,
        'image': recipe.image,
        'description': recipe.description,
        'ingredients': recipe.ingredients.order_by('name'),
    }
    return render(request, 'recipe_catalog/recipe.html', context)


def handle_error_404(request):
    return render(request, 'recipe_catalog/404.html', status=404)


def form_user_test(request):
    """Test form for user"""
    if request.GET:
        form = UserForm(request.GET)
        if form.is_valid():
            pass
    else:
        form = UserForm()
    context = {'form': form}
    return render(request, 'recipe_catalog/form_user_test.html', context)


@login_required
def ingredient(request):
    form = IngredientForm(request.POST or None)
    if form.is_valid():
        form.save()
    context = {'form': form}
    return render(request, 'recipe_catalog/ingredient_form.html', context)


def ingredient_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('recipe_catalog:login')
    instance = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        form = IngredientForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('recipe_catalog:ingredients')
    else:
        form = IngredientForm(instance=instance)
    context = {'form': form}
    return render(request, 'recipe_catalog/ingredient_form.html', context)


def ingredients(request):
    ingredients = Ingredient.objects.all()
    context = {'ingredients': ingredients}
    return render(request, 'recipe_catalog/ingredients.html', context)


def ingredient_delete(request, pk):
    instance = get_object_or_404(Ingredient, pk=pk)
    form = IngredientForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('recipe_catalog:ingredients')
    return render(request, 'recipe_catalog/ingredient_form.html', context)


@login_required
def recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            form.save_m2m()
            return redirect('recipe_catalog:recipe_detail', pk=instance.pk)
    else:
        form = RecipeForm()
    context = {'form': form}
    return render(request, 'recipe_catalog/recipe_form.html', context)


def recipe_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('recipe_catalog:login')
    instance = get_object_or_404(Recipe, pk=pk)
    if instance.author != request.user:
        # raise PermissionDenied
        return HttpResponse('You can not edit this recipe')
    form = RecipeForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('recipe_catalog:recipe_detail', pk=instance.pk)
    context = {'form': form}
    return render(request, 'recipe_catalog/recipe_form.html', context)


@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    form = RecipeForm(instance=recipe)
    context = {'form': form}
    if request.method == 'POST':
        if recipe.author != request.user:
            raise PermissionDenied
        else:
            recipe.delete()
            return redirect('recipe_catalog:index')
    return render(request, 'recipe_catalog/recipe_form.html', context)
