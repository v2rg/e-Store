from django import forms


class OrderForm(forms.ModelForm):
    first_name = ...
    last_name = ...
    postal_code = ...
    city = ...
    street = ...
    building_number = ...
    apartment_number = ...
