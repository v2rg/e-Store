# from django.core.exceptions import ValidationError
#
#
# # валидатор для поля 'postcode' (UserAddressForm)
# def validate_positive_integer(value):
#     print(type(value))
#     if not isinstance(value, int):
#         raise ValidationError(
#             message='Можно вводить только цифры', params={'value': value}
#         )
#     return value
