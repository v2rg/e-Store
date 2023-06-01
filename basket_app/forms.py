from django import forms

from users_app.models import User, UserAddress


# class OrderConfirmationForm(forms.ModelForm):
#     first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}))
#     last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
#
#     postcode = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Индекс'}))
#     city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город'}))
#     street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Улица'}))
#     building = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Дом'}))
#     floor = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Этаж'}))
#     apartment = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Квартира'}))
#
#     comment = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Комментарий'}))
#
#     class Meta:
#         model = UserAddress
#         fields = '__all__'
