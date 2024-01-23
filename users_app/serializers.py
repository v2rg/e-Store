import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from basket_app.models import Order, OrderItem
from users_app.models import User, UserAddress


class UserRegistrationSerializer(serializers.ModelSerializer):  # API регистрация пользователя
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(label='Повтор пароля', write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        password = attrs['password']

        if len(password) < 8:
            raise serializers.ValidationError({'password': 'Пароль должен быть не менее 8 символов'})
        if password.isdigit():
            raise serializers.ValidationError({'password': 'Пароль должен содержать не только цифры'})
        if not re.findall('\d', password):  # \d — одна цифра
            raise serializers.ValidationError({'password': 'Пароль должен содержать цифры'})
        if not re.findall('[a-z]', password):
            raise serializers.ValidationError({'password': 'Пароль должен содержать буквы'})
        if not re.findall('\W', password):  # \W — один спецсимвол
            raise serializers.ValidationError({'password': 'Пароль должен содержать спецсимволы'})
        if password != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password'])  # пробуем хэшировать пароль
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):  # API профиль пользователя
    email = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar']


class UserAddressSerializer(serializers.ModelSerializer):  # API адрес пользователя
    class Meta:
        model = UserAddress
        fields = ['postcode', 'city', 'street', 'building', 'floor', 'apartment']


class UserOrdersSerializer(serializers.ModelSerializer):  # API список заказов пользователя
    user_id = serializers.SlugRelatedField(slug_field='username', read_only=True)

    # created_datetime = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    # updated_datetime = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Order
        fields = ['user_id', 'first_name', 'last_name',
                  'postcode', 'city', 'street',
                  'building', 'floor', 'apartment',
                  'created_datetime', 'updated_datetime', 'status',
                  'paid', 'total_quantity', 'total_sum', 'comment']

    def validate(self, attrs):
        if attrs['postcode'].isdigit():
            raise serializers.ValidationError({'postcode': 'Можно вводить только цифры'})


class UserOrderSerializer(serializers.ModelSerializer):  # API содержимое заказа
    product_category = serializers.SlugRelatedField(slug_field='category_name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['order_id', 'product_category', 'product_sku', 'quantity', 'price']
