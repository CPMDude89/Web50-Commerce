from django import forms
from django.forms import ModelForm


from .models import Listing

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['name', 'starting_bid', 'category', 'description', 'image']


# looks for a listing, returns the pk (int, not an object) of a listing
def listingSearch(query):
    # create a QuerySet
    listings = Listing.objects.all()
    # iterate over all the listings
    for listing in listings:
        # make the search case-insensitive
        if query.casefold() == listing.name.casefold():
            # return the primary key of the listing
            return listing.pk

    # if no match is found, just return False
    return False