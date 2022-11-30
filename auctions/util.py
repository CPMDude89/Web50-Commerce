from .models import Listing

def listingSearch(query):
    listings = Listing.objects.all()
    for listing in listings:
        if query.casefold() == listing.name.casefold():
            pk = listing.pk
            return pk

    return False
    