import json

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import View
from rest_framework import viewsets
from django import template
from .forms import RecipeForm
from .models import Recipe, Ingredient, RecipeIngredient, User, Follow, Tag
from rest_framework.decorators import api_view, renderer_classes
from django.contrib.auth.decorators import login_required
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def get_ingredients(request):
    query = request.GET.get('query')
    queryset = Ingredient.objects.filter(title__startswith=query)
    ing_list = []
    for item in queryset:
        dict_response = {"title": item.title, "dimension": item.dimension}
        ing_list.append(dict_response)
    return JsonResponse(ing_list, safe=False)


def get_ingredients_for_recipe_form(query_data):
    ingredients = [
        query_data[key]
        for key in query_data.keys()
        if key.startswith("nameIngredient")
    ]
    amounts = [
        query_data[key]
        for key in query_data.keys()
        if key.startswith("valueIngredient")]

    result = zip(ingredients, amounts)

    return result


def index(request):
    recipes = Recipe.objects.all()
    paginator = Paginator(recipes, 6)
    image = Recipe.image
    page_number = request.GET.get('page')
    breakfast = request.GET.get('breakfast')
    lunch = request.GET.get('lunch')
    dinner = request.GET.get('dinner')
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:
        return render(request, 'indexAuth.html', {
            'page': page,
            'paginator': paginator,
            'image': image,
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
        })
    else:
        return render(request, 'indexNotAuth.html', {
            'page': page,
            'paginator': paginator,
            'image': image,
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
        })


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        ingredients = get_ingredients_for_recipe_form(request.POST)

        if form.is_valid():
            if request.user.is_authenticated:
                recipe = form.save(commit=False)
                recipe.author = request.user
                # form_dict = request.POST
                # for tag in tags:
                #     if tag in form_dict:
                #         recipe.tags = form_dict[tag]
                recipe.save()
                for (item, amount) in ingredients:
                    RecipeIngredient.objects.create(
                        ingredient=Ingredient.objects.get(title=f"{item}"),
                        amount=amount,
                        recipe=recipe,
                    )
                form.save_m2m()
                return redirect('index')
            return redirect('/auth/login')
    return render(request, "formRecipe.html", {"form": form, })


def subscriptions(request):
    print(request.body)
    print('пост пост')

    reg = json.loads(request.body)
    user_id = reg.get("id", None)
    author = get_object_or_404(User, id__exact=user_id)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)
        return JsonResponse({"success": True})
    # paginator = Paginator(recipes, 6)
    # page_number = request.GET.get('page')
    # page = paginator.get_page(page_number)
    # return render(request, 'myFollow.html', {
    #     # 'page': page,
    #     # 'paginator': paginator
    # })


def recipe_page(request, recipe_id):
    recipe = get_object_or_404(Recipe,
                               id__exact=recipe_id)
    image = recipe.image
    author = recipe.author
    cooking_time = recipe.cooking_time
    ingredients = RecipeIngredient.objects.filter(recipe_id=recipe_id)
    description = recipe.text
    if request.user.is_authenticated:
        return render(request, "singlePage.html", {
            "recipe": recipe,
            "author": author,
            "image": image,
            "cooking_time": cooking_time,
            "ingredients": ingredients,
            "description": description,

        })
    else:
        return render(request, "singlePageNotAuth.html", {
            "recipe": recipe,
            "author": author,
            "image": image,
            "cooking_time": cooking_time,
            "ingredients": ingredients,
            "description": description,

        })


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect("index")
    form = RecipeForm(
        request.POST or None, files=request.FILES or None, instance=recipe
    )
    if request.method == "POST":
        ingredients = get_ingredients_for_recipe_form(request.POST)
        if form.is_valid():
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            for (item, amount) in ingredients:
                RecipeIngredient.objects.create(
                    ingredient=Ingredient.objects.get(title=f"{item}"),
                    amount=amount,
                    recipe=recipe,
                )
            form.save_m2m()
        return redirect("/")

    return render(
        request, "formChangeRecipe.html", {"form": form, "recipe": recipe, "recipe_id": recipe_id, },
    )


def profile(request, username):
    user = get_object_or_404(User, username__exact=username)
    user_id = user.id
    user_name = user.first_name
    recipes = Recipe.objects.filter(author=user_id)
    paginator = Paginator(recipes, 6)
    image = Recipe.image
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        return render(request, "authorRecipe.html", {
            'page': page,
            'paginator': paginator,
            'image': image,
            'name': user_name,
        })
    else:
        return render(request, "authorRecipeNotAuth.html", {
            'page': page,
            'paginator': paginator,
            'image': image,
            'name': user_name,
        })


@login_required
@csrf_exempt
def profile_follow(request):
    following = Follow.objects.filter(user=request.user).values('author')
    recipes = Recipe.objects.filter(author__in=following)
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'myFollow.html', {
        'following': following,
        'recipes': recipes,
        'page': page,
        'paginator': paginator
    })


@login_required
def purchases(request):
    return render(request, 'shopList.html')


def favorites(request, recipe_id=None):
    print(request.body)
    print('пост пост')

    reg = json.loads(request.body)
    user_id = reg.get("id", None)
    print(user_id)
    # author = get_object_or_404(User, id__exact=user_id)
    # if request.user != author:
    #     Follow.objects.get_or_create(author=author, user=request.user)
    return JsonResponse({"success": True})


def favorite_recipes(request):
    return render(request, "favorite.html")
