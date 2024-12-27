from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'recipe_catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/', views.recipe, name='recipe'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('about/', views.about, name='about'),
    path('form_user_test/', views.form_user_test, name='create_user_test'),
    path('ingredients/', views.ingredients, name='ingredients'),
    path('ingredient/', views.ingredient, name='ingredient'),
    path(
        'ingredient/<int:pk>/edit/',
        views.ingredient_edit,
        name='ingredient_edit'
    ),
    path(
        'ingredient/<int:pk>/delete/',
        views.ingredient_delete,
        name='ingredient_delete'
    ),
    path('auth/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
