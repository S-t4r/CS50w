import bleach
import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import Posts, User


def index(request):
    posts = Posts.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def new_post(request):
    if request.method == "POST":
        content = request.POST["new_post"]

        # If content is empty
        if content == "":
            return render(request, "network/index.html", {
                "message": "Post cannot be empty."
            })
        
        user = request.user

        # Create new post
        try:
            post = Posts.objects.create(content=content, user=user)
            post.save()
        except IntegrityError:
            return render(request, "network/index.html", {
                "message": "Something went wrong when posting."
            })
        
        return redirect("index")


def likes(request):
    if request.method == "POST":
        user = request.user
        data = json.loads(request.body)
        post_id = data["post_id"]

        with transaction.atomic():
            post = Posts.objects.select_for_update().get(id=post_id)
            has_liked = post.likes.filter(id=user.id).exists()

        # If user is liking the post
        if not has_liked:
            post.likes.add(user)
        # If user is un-liking the post
        else:
            post.likes.remove(user)
        
        post.save()

        return JsonResponse({'success': 'Post updated successfully', 'new_like_count': post.likes.count()})



def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = user.user_posts.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/user_profile.html", {
        "user": user,
        "page_obj": page_obj,
    })
    



def follow(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        # Check if user is in followers
        is_follower = target_user.followers.filter(id=request.user.id).exists()

        # If hasn't yet followed
        if not is_follower:
            target_user.followers.add(request.user)
        else:
            target_user.followers.remove(request.user)
        
        return redirect("user_profile", user_id=user_id)



def following(request):
    user = get_object_or_404(User, id=request.user.id)
    following_users = user.following.all()
    following_posts = Posts.objects.filter(user__in=following_users).order_by("-timestamp")
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })



def edit(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        content = data.get('content')
        if not content:
            return JsonResponse({'error': "Content must be a string"}, status=400)
        
        if not isinstance(content, str):
            return JsonResponse({'error': 'Content must be a string'}, status=400)
        
        content = bleach.clean(content)

        if len(content) > 500:
            return JsonResponse({'error': 'Content is too long'}, status=400)
        
        post = Posts.objects.get(id=post_id)
        post.content = content
        post.save()

        return JsonResponse({'success': 'Post updated successfully', 'content': post.content}, status=200)






