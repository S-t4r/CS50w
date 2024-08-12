from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    CATEGORY_CHOICES = [
        ('TOYS', 'Toys'),
        ('BOOK', 'Books'),
    ]
    category = models.CharField(max_length=4, choices=CATEGORY_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lister")
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.FloatField()
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="winner")

    
    def __str__(self):
        return f"{self.title}, {self.description}, {self.starting_bid}"


class Bid(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder}: ${self.amount} on {self.auction.title}, at {self.timestamp.strftime('%H:%M')}"
    


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()

    def __str__(self):
        return f"{self.user} commented =>>>: {self.text}"


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.listing.title}, {self.listing.starting_bid}"