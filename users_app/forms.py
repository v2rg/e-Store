from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from users_app.models import User, UserAddress
from users_app.tasks import send_verification_email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя', 'autofocus': True}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите эл. почту'}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=True)
        send_verification_email.delay(user.id)
        return user


class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Имя'}))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Имя пользователя', 'readonly': True}), required=False)
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Адрес электронной почты', 'readonly': True}),
        required=False)
    avatar = forms.ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'placeholder': 'Аватар'}), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'avatar')


class UserAddressForm(forms.ModelForm):
    postcode = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Индекс'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город'}))
    street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Улица'}))
    building = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Дом'}))
    floor = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Этаж'}),
                            required=False)
    apartment = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Квартира'}),
                                required=False)

    class Meta:
        model = UserAddress
        fields = ('postcode', 'city', 'street', 'building', 'floor', 'apartment')
