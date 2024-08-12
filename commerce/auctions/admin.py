from django.contrib import admin
from .models import AuctionListing, Bid, Comment, WatchList

# Register your models here.
def close_auctions(modeladmin, request, queryset):
    for auction in queryset:
        highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.bidder

        auction.active = False
        auction.save()
        WatchList.objects.filter(listing=auction).delete()


def active_auctions(modeladmin, request, queryset):
    for auction in queryset:
        auction.winner = None
        auction.active = True
        auction.save()


def declare_winner(modeladmin, request, queryset):
    for auction in queryset:
        highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.bidder
            auction.active = False
            auction.save()

            WatchList.objects.filter(listing=auction).delete()


class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'starting_bid', 'active')
    actions = [close_auctions, declare_winner, active_auctions]

declare_winner.short_description = "Declare winner for selected auctions"
close_auctions.short_description = "Close selected auctions"
active_auctions.short_description = "Activate a listing"




admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)