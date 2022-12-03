from django import forms
from django.forms import ModelForm


from .models import Listing, Bid, Comment, Category

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['name', 'starting_bid', 'category', 'description', 'image', 'user']
        widgets = {
            'user': forms.HiddenInput()
        }

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['user', 'amount', 'listing']
        # we will fill in these fields in the view layer. User just needs to submit the bid amount
        widgets = {
            'user': forms.HiddenInput(),
            'listing': forms.HiddenInput()
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['user', 'text', 'listing']
        labels = {'text': ""}
        widgets = {
            'user': forms.HiddenInput(),
            'listing': forms.HiddenInput()
        }

class CategoriesForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']

""""
class CloseListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['name','active', 'user_winner']
        widgets = {
            'name': forms.HiddenInput(),
            'active': forms.HiddenInput(),
            'user_winner': forms.HiddenInput()
        }    
"""

class CloseListingForm(forms.Form):
    user_winner = forms.CharField(max_length=512, widget=forms.HiddenInput(), required=False)

class AddRemoveWatchlistForm(forms.Form):
    in_list = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    listing = forms.CharField(max_length=64, widget=forms.HiddenInput())


# looks for a listing, returns the pk (int, not an object) of a listing
def listingSearch(query):
    # create a QuerySet filtered with a case insensitive name query
    try: 
        listing = Listing.objects.get(name__iexact=query)
        return listing.pk
    except:
        return False