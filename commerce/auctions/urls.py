from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("active_listings/", views.active_listings, name="active_listings"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("create", views.create, name="create"),
    path("create_comment/<int:id>", views.create_comment, name="create_comment"),
    path("add_to_watchlist/<int:id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("remove_listing/<int:id>", views.remove_listing, name="remove_listing"),
    path("close_listing/<int:id>", views.close_listing, name="close_listing"),
    path("bid_listing/<int:id>", views.bid_listing, name="bid_listing"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category_name>/", views.category_detail, name="category_detail"),
    path("closed_listings/", views.closed_listings, name="closed_listings")
]
