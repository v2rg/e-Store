from django import forms

from reviews_app.models import ProductReview


class ProductReviewForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    rating = forms.ChoiceField(choices=((x, str(x)) for x in range(5, 0, -1)),
                               widget=(forms.Select(attrs={'class': 'form-select'})), required=False)  # не обязательно

    class Meta:
        model = ProductReview
        fields = ('review', 'rating')
