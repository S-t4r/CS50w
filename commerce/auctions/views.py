from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse


from .models import AuctionListing, Bid, Comment, User, WatchList
from .forms import AuctionListingForm

def index(request):
    """
    Show a list of all my biddings
    """
    if request.user.is_authenticated:
        user_bids = Bid.objects.filter(bidder=request.user).order_by('-timestamp')
    else:
        user_bids = []
    return render(request, "auctions/index.html", {
        "user_bids": user_bids
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



def active_listings(request):
    """
    Show a list of active listings
    """
    # Get auction by id
    active_listing = AuctionListing.objects.filter(active=True)

    if request.user.is_authenticated:
        user_bids = Bid.objects.filter(bidder_id=request.user).values_list('auction', flat=True)
    else:
        user_bids = []

    # Pass the auction listing to the template
    return render(request, "auctions/active_listings.html", {
        "active_listing": active_listing,
        "user": request.user,
        "user_bids": user_bids
    })



def closed_listings(request):
    """
    Show a list of closed listings
    """
    closed_listings = AuctionListing.objects.filter(active=False)
    
    return render(request, "auctions/closed_listings.html", {
        "closed_listing": closed_listings
    })


def listing(request, id):
    """
    A unique page for each listing
    """
    form = AuctionListing.objects.get(pk=id)
    comments = Comment.objects.filter()
    bids = Bid.objects.filter(auction=form).order_by('-amount')
    winner = form.winner

    return render(request, "auctions/listing.html", {
        "form": form,
        "user": request.user,
        "comments": comments,
        "bids": bids,
        "winner": winner,
    })


@login_required
def create(request):
    """
    Create new listing.
    """
    # POST
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)

            # Pass in user to be saved in the object.
            listing.user = request.user
            listing = form.save()
            return redirect('listing', id=listing.pk)
    
    # GET
    else:
        form = AuctionListingForm()
        return render(request, "auctions/create.html", {
            "form": form,
        })
    

@login_required
def create_comment(request, id):
    """
    Create a comment on a listing
    """
    if request.method == "POST":
        text = request.POST.get("comment")
        listing = get_object_or_404(AuctionListing, pk=id)
        if text:
            Comment.objects.create(user=request.user, listing=listing, text=text)
            return redirect('listing', id=id)
        else:
            # If message is None show error
            messages.error(request, "Comment cannot be empty.")
            return redirect('listing', id=id)
            
        

@login_required
def add_to_watchlist(request, id):
    """
    Add an item to the watch list.
    """
    listing = get_object_or_404(AuctionListing, pk=id)
    if not WatchList.objects.filter(user=request.user, listing=listing).exists():
        WatchList.objects.create(user=request.user, listing=listing)
        return redirect('listing', id=id)
    # Cannot add the same item to the watch list twice
    else:
        messages.error(request, "Item is already in Watch List.")
        return redirect('listing', id=id)
        

@login_required
def watchlist(request):
    """
    Render watch list.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        WatchList.objects.filter(pk=item_id, user=request.user).delete()

        # Fetch updated list
        watchlist = WatchList.objects.filter(user=request.user)
        return render(request, "auctions/watch_list.html", {
            "watchlist": watchlist,
        })

    else:
        watchlist = WatchList.objects.filter(user=request.user)
        return render(request, "auctions/watch_list.html", {
            "watchlist": watchlist,
        })


@login_required
def remove_listing(request, id):
    """
    Remove a listing from database.
    """
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=id)
        listing.delete()
        return redirect('active_listings')
    

@login_required
def close_listing(request, id):
    """
    Close an Auction
    """
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=id)
        listing.active = False
        highest_bid = Bid.objects.filter(auction=listing).order_by('-amount').first()
        listing.winner = highest_bid.bidder
        listing.save()

        # Remove the listing from all watch lists
        WatchList.objects.filter(listing=listing).delete()

        return redirect('listing', id=id)
    

@login_required
def bid_listing(request, id):
    """
    Bid higher
    """
    try:
        bid = float(request.POST.get('bid'))
    
    except ValueError:
        messages.error(request, "Enter a Number.")
        return redirect('listing', id=id)
    
    listing = get_object_or_404(AuctionListing, pk=id)

    if (bid >= listing.starting_bid + 1):
        listing.starting_bid = bid
        listing.save()

        # Create a new Bid instance
        Bid.objects.create(auction=listing, bidder=request.user, amount=bid)

        if not WatchList.objects.filter(user=request.user, listing=listing).exists():
            WatchList.objects.create(user=request.user, listing=listing)

        return redirect('listing', id=id)
    else:
        messages.error(request, "You must bid 1$ higher than the current bid.")
        return redirect('listing', id=id)
    


def categories(request):
    categories = AuctionListing.CATEGORY_CHOICES
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })


def category_detail(request, category_name):
    active_listing = AuctionListing.objects.filter()
    return render(request, 'auctions/category_detail.html', {
        'active': active_listing,
        'category_name': category_name
    })
