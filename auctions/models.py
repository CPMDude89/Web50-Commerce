from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# auction listings
class Listing(models.Model):
    # name of the listing to be auctioned
    name = models.CharField(max_length=64)
    # starting bid amount
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10)
    # category of listing
    category = models.CharField(max_length=64, blank=True)
    # a text field description to be displayed with the listing
    description = models.TextField(max_length=512)
    # image of the listing -- OPTIONAL
    image = models.ImageField(upload_to="auctions/", blank=True)
    # is the listed item currently active (able to be bid on)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


# bids to be made on the listings
class Bid(models.Model):
    # username of bidder on this particular bid, should be inserted into a new bid by code, not by user
    bidder = models.CharField(max_length=150)
    # amount of $ bidded
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    # listing that this bid was made on
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    # time and date when this bid was bid
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.bidder} has entered a bid of ${self.amount} at {self.date}"


# comments to be left on each bid
class Comment(models.Model):
    # username of user who wrote the comment, should be inserted into a new bid by code, not by user
    commenter = models.CharField(max_length=150, blank=True)
    # the comment text
    text = models.TextField(max_length=512)
    # listing that this comment was left on
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", blank=True)
    # time and date when comment was left
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.commenter} left a comment on {self.listing} at {self.date}"