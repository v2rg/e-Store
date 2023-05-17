from django.db import models

# Create your models here.

from basket_app import views


class UserOrder(models.Model):
    order_id = ...
