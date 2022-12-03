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


# handles the listing page. There's got to be a way to do this more efficiently, but it works ----------------------
def listing_view(request, listing_name):
    # ------ first things first, get the listing  
    findListing = listingSearch(listing_name)
    # check if listing exists
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
        if request.method == "POST" and 'bform_button' in request.POST: # if BidForm button was clicked
            # validate incoming form (bid) data
            bform = BidForm(request.POST)
            if bform.is_valid():
                bform.save()
                bform = BidForm(initial={'user': request.user, 'listing': listing}) # instantiate a new BidForm so user can keep bidding on same page
            else:
                bform = BidForm(request.POST) # error handling
        # GET request
        else: 
            bform = BidForm(initial={'user': request.user, 'listing': listing})

        # --- COMMENTS ---
        if request.method == "POST" and "cform_button" in request.POST: # if CommentForm button was clicked
            # validate incoming form (comment) data
            cform = CommentForm(request.POST)
            if cform.is_valid():
                cform.save()
                cform = CommentForm(initial={'user': request.user, 'listing': listing}) # instantiate a new CommentForm so user can keep commenting on same page
            else:
                cform = CommentForm(request.POST) # error handling
        # GET request
        else:
            cform = CommentForm(initial={'user': request.user, 'listing': listing})

        # --- CLOSE LISTING ---
        if request.method == "POST" and 'closeform_button' in request.POST: # if close listing button was clicked
            closeform = CloseListingForm(request.POST) 
            if closeform.is_valid():
                listing.active = False
                winner = User.objects.get(username=closeform.cleaned_data['user_winner'])
                listing.user_winner = winner # just a variable for the template
                listing.save()
            else:
                closeform = CloseListingForm(request.POST) # error handling
                listing_active = listing.active # just a template variable
        
        # GET request
        else:
            # if NO BIDS have been placed on this listing, don't allow user to close listing
            if not listing.bids.all(): 
                closeform = CloseListingForm() # form is instantiated without a winner, so no user can be assigned winner
                listing_active = listing.active
            # if at least one BID has been placed, listing can be closed
            else:
                winner = listing.bids.last().user
                # instantiate the form with the user who made the highest bid so if the form is sent via POST, it will contain the winner 
                closeform = CloseListingForm(initial={'user_winner': winner}) 
                listing_active = listing.active

        listing_active = listing.active # I think this needs to be here if a successful closeform has been submitted

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
        
        # -------- if user IS AUTHENTICATED
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

    # ------ if user is NOT AUTHENTICATED ---
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
        


# user can add or remove listings to a specific page that will display them --------------
@login_required
def watchlist(request):
    # first things first, get the watchlist for the user
    w_list = Watchlist.objects.get(user=request.user)

    # handle incoming POST request to either add or remove a listing from watchlist
    if request.method == 'POST':
        form = AddRemoveWatchlistForm(request.POST)
        if form.is_valid():
            in_list = form.cleaned_data["in_list"] # a boolean that tells us if the listing is in the user's watchlist or not
            listingTarget = Listing.objects.get(name__iexact=form.cleaned_data["listing"])

            # check if the listing in question is in the list, and either take it out or add it in
            if in_list:
                w_list.listings.remove(listingTarget)
            else:
                w_list.listings.add(listingTarget)

    # creates a new QuerySet for the template to use, if any changes were made, they will be reflected here now
    listings = w_list.listings.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

# if a user is logged in, they can make a new listing -------------
@login_required
def new_listing(request):
    # handle form submission - POST request
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() # save a new listing 
            return HttpResponseRedirect(reverse("index")) # redirect back to homepage
        else:
            return render(request, "auctions/new_listing.html", {
                "form": form # returns the form back to the browser
            })
    
    else:
        form = NewListingForm(initial={'user': request.user})
        return render(request, "auctions/new_listing.html", {
            "form": form
        })

# really just here for debugging... -------------
def all_listings(request):
    listings = Listing.objects.all()

    return render(request, "auctions/all_listings.html", {
        'listings': listings
    })

# list all categories, if a user is logged in, they can make a new one --------------
def categories(request):
    categories_list = Category.objects.all()

    # if a user tries to make a new category
    if request.method == "POST":
        form = CategoriesForm(request.POST)
        if form.is_valid():
            form.save()
            form = CategoriesForm()
        else:
            form = CategoriesForm(request.POST)
    
    # GET request
    else:
        form = CategoriesForm() 

    return render(request, "auctions/categories.html", {
        'categories_list': categories_list,
        'form': form
    })

# list all active listings under a specific category ----------------
def category_listings(request, category_name):
    # first things first, get the category
    category_ = Category.objects.get(name=category_name)
    listings = Listing.objects.filter(category=category_) # <--- not sure if I need to be careful like this with the 'category' variable. Probably not, but just to be safe...

    # check if there are any active listings under this category
    # if so, assign the queryset to a listings variable to use in the template
    checkActive = listings.filter(active=True)
    if checkActive:
        anyActive = True
        listings = checkActive
    else:
        anyActive = False

    return render(request, "auctions/category_listings.html", {
        'listings': listings,
        'anyActive': anyActive,
        'category': category_
    })