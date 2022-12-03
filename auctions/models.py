from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    pass



# auction listings

# categories for users to choose to add to a listing
class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    # name of the listing to be auctioned
    name = models.CharField(max_length=64, unique=True)
    # starting bid amount
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10)
    # category of listing
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", blank=True, null=True)
    # a text field description to be displayed with the listing
    description = models.TextField(max_length=512)
    # image of the listing -- OPTIONAL
    image = models.ImageField(upload_to="auctions/", blank=True)
    # user who created the listing
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    # user who 'won' the auction listing
    user_winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_won", blank=True, null=True)
    # is the listed item currently active (able to be bid on)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    # double check listing name uniqueness by checking case 
    
    def clean(self):
        allNames = Listing.objects.filter(name__iexact=self.name).exclude(name__exact=self.name)
        if allNames:
            raise ValidationError("A listing's name must be unique, regardless of case!!")
            


# bids to be made on the listings
class Bid(models.Model):
    # user who made this particular bid
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    # amount of $ bidded
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    # listing that this bid was made on
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    # time and date when this bid was bid
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.user.username} has entered a bid of ${self.amount} on {self.listing.name}"

    def clean(self):
        if self.amount < self.listing.starting_bid:
            raise ValidationError('Each bid must be at least as large as the starting price.')

        all_bids = self.listing.bids.all()
        for bid in all_bids:
            if self.amount <= bid.amount:
                raise ValidationError('Each bid must be higher than the current highest bid.')
                


# comments to be left on each bid
class Comment(models.Model):
    # user who made this particular bid
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    # the comment text
    text = models.TextField(max_length=512)
    # listing that this comment was left on
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", blank=True)
    # time and date when comment was left
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.user.username} left a comment on {self.listing} at {self.date}"

# a user's watchlist so they can keep track of listings they like
class Watchlist(models.Model):
    # who's watchlist this is
    user = models.ForeignKey(User, related_name="watchlist", on_delete=models.CASCADE, null=True)   
    # listings in the watchlist
    listings = models.ManyToManyField(Listing, related_name="watchlists", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} has a watchlist"
