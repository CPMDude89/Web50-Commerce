from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .util import listingSearch, NewListingForm, AddRemoveWatchlistForm, BidForm, CommentForm, CloseListingForm, CategoriesForm

from .models import User, Listing, Watchlist, Category



def index(request):
    activeList = Listing.objects.filter(active=True)


    return render(request, "auctions/index.html", {
        "activeList": activeList
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
            user_ = User.objects.create_user(username, email, password)
            user_.save()
            wlist = Watchlist(user=user_)
            wlist.save()

        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user_)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing_view(request, listing_name):
    # ------ first things first, get the listing  
    findListing = listingSearch(listing_name)
    if findListing:
        listing = Listing.objects.get(pk=findListing) # remember, listingSearch() returns an int -- which is a pk
    else:
        return render(request, "auctions/not_found.html")

    # ------ set up forms for user to use if they are logged in
    if request.user.is_authenticated:
        
        # --- WATCHLIST ---
        w_list = Watchlist.objects.get(user=request.user)
        w_listings = w_list.listings.all()

        # if the item IS in user's watchlist
        if listing in w_listings:
            message = "This item is in your watchlist!"
            button_message = "Click here to remove it"
            wform = AddRemoveWatchlistForm(initial={'in_list': True, 'listing': listing.name})
        # if the item IS NOT in the user's watchlist
        else:
            message = "This item is NOT in your watchlist!"
            button_message = "Click here to add it"
            wform = AddRemoveWatchlistForm(initial={'in_list': False, 'listing': listing.name})

        # --- BIDS ---
        if request.method == "POST" and 'bform_button' in request.POST:
            # validate incoming form (bid) data
            bform = BidForm(request.POST)
            if bform.is_valid():
                bform.save()
                bform = BidForm(initial={'user': request.user, 'listing': listing})
            else:
                bform = BidForm(request.POST)
        else: 
            bform = BidForm(initial={'user': request.user, 'listing': listing})

        # --- COMMENTS ---
        if request.method == "POST" and "cform_button" in request.POST:
            # validate incoming form (comment) data
            cform = CommentForm(request.POST)
            if cform.is_valid():
                cform.save()
                cform = CommentForm(initial={'user': request.user, 'listing': listing})
            else:
                cform = CommentForm(request.POST)
        else:
            cform = CommentForm(initial={'user': request.user, 'listing': listing})

        # --- CLOSE LISTING ---
        if request.method == "POST" and 'closeform_button' in request.POST:
            closeform = CloseListingForm(request.POST)
            if closeform.is_valid():
                listing.active = False
                winner = User.objects.get(username=closeform.cleaned_data['user_winner'])
                listing.user_winner = winner
                listing.save()
            else:
                closeform = CloseListingForm(request.POST)
                listing_active = listing.active
        
        else:
            if not listing.bids.all():
                closeform = CloseListingForm()
                listing_active = listing.active
            else:
                winner = listing.bids.last().user
                closeform = CloseListingForm(initial={'user_winner': winner})
                listing_active = listing.active

        listing_active = listing.active # <--- ????

        # determine if the current logged in user is the user who made this listing
        if request.user == listing.user: 
            is_users_listing = True
        else:
            is_users_listing = False

        # determine if the current logged in user has 'won' this listing
        if request.user == listing.user_winner:
            is_listing_winner = True
        else:
            is_listing_winner = False

        # ------ set up the bids and comments to be added into page context
        highest_bid = listing.bids.last()
        comments = listing.comments.all()
        
        return render(request, "auctions/listing.html", {
            "listing": listing,
            'highest_bid': highest_bid,
            "comments": comments,
            "message": message,
            "button_message": button_message,
            "wform": wform,
            'bform': bform,
            'cform': cform,
            'closeform': closeform,
            'is_users_listing': is_users_listing,
            'is_listing_winner': is_listing_winner,
            'listing_active': listing_active
        })

    # ------ if user is NOT authenticated ---
    else:
        bids = listing.bids.all()
        highest_bid = listing.bids.last()
        comments = listing.comments.all()
        is_users_listing = False
        
        return render(request, "auctions/listing.html", {
            "listing": listing,
            'highest_bid': highest_bid,
            "bids": bids,
            "comments": comments,
            'is_users_listing': is_users_listing
        })
        

@login_required
def watchlist(request):
    # get the watchlist first, we'll need it no matter what
    w_list = Watchlist.objects.get(user=request.user)

    # use a http POST request to alter the state of the user's watchlist
    if request.method == 'POST':
        form = AddRemoveWatchlistForm(request.POST)
        if form.is_valid():
            in_list = form.cleaned_data["in_list"]
            listingTarget = Listing.objects.get(name__iexact=form.cleaned_data["listing"])

            # check if the listing in question is in the list, and either take it out or add it in
            if in_list:
                w_list.listings.remove(listingTarget)
            else:
                w_list.listings.add(listingTarget)

    # creates a new QuerySet, so we don't need to recreate the watchlist entirely here if some changes were made
    listings = w_list.listings.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def new_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new_listing.html", {
                "form": form
            })
    
    else:
        form = NewListingForm(initial={'user': request.user})
        return render(request, "auctions/new_listing.html", {
            "form": form
        })

def all_listings(request):
    listings = Listing.objects.all()

    return render(request, "auctions/all_listings.html", {
        'listings': listings
    })

def categories(request):
    categories_list = Category.objects.all()

    if request.method == "POST":
        form = CategoriesForm(request.POST)
        if form.is_valid():
            form.save()
            form = CategoriesForm()
        else:
            form = CategoriesForm(request.POST)
    
    else:
        form = CategoriesForm()

    return render(request, "auctions/categories.html", {
        'categories_list': categories_list,
        'form': form
    })

def category_listings(request, category_name):
    # first things first, get the category
    category_ = Category.objects.get(name=category_name)
    listings = Listing.objects.filter(category=category_)

    checkActive = listings.filter(active=True)
    if checkActive:
        anyActive = True
        listings = checkActive
    else:
        anyActive = False

    return render(request, "auctions/category_listings.html", {
        'listings': listings,
        'anyActive': anyActive
    })