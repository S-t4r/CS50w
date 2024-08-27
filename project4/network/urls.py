
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("likes", views.likes, name="likes"),
    path("user/<int:user_id>/", views.user_profile, name="user_profile"),
    path("follow/<int:user_id>/", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("edit/<int:post_id>/", views.edit, name="edit")
]
