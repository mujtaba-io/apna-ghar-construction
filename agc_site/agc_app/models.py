import datetime
import random

import django
from django.db import models

#--- COMMENT: model is simply a database layout. all values to database are added according to this
#--- layout.

""" from django documantation:

Here, each model is represented by a class that subclasses django.db.models.Model.
Each model has a number of class variables, each of which represents a database field in the model.

Each field is represented by an instance of a Field class – e.g., CharField for character fields and
DateTimeField for datetimes. This tells Django what type of data each field holds.

The name of each Field instance (e.g. question_text or pub_date) is the field’s name,
in machine-friendly format. You’ll use this value in your Python code, and your database will use it
as the column name.

note, a relationship is defined using ForeignKey.
"""

# .................................................................
# .................................................................

# Registered Users
class User(models.Model):
    type = models.IntegerField(default=0) # types: 0=client,1=contractor,2=corporate

    name = models.CharField(max_length=32, default='')
    username = models.CharField(max_length=32, default='')
    email = models.EmailField(default='')
    contact_number = models.CharField(default='', max_length=32)
    password = models.CharField(max_length=32, default='')

    photo = models.ImageField(upload_to='profile_photos/', default='')

    offerings = models.TextField(default='')  # For CONTRACTOR ONLY

    # TODO: ADD LOCATION

    @property
    def profile_photo(self):
        if self.photo: return self.photo.url
        else: return '/static/avatar.png'

    def __str__(self):
        return self.username

    @property
    def positive_reviews_count(self):
        return Review.objects.filter(to_user=self, is_positive=True).count()

    @property
    def negative_reviews_count(self):
        return Review.objects.filter(to_user=self, is_positive=False).count()

    @property
    def contracts_count(self):
        return Contract.objects.filter(to_user=self).count()

    @property
    def transactions_count(self):
        return Transaction.objects.filter(to_user=self).count()

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Contract with contractor, for their services
class Contract(models.Model):
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_by_user_set')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_to_user_set')

    description = models.TextField(default='')
    site_address = models.CharField(default='', max_length=512)
    date = models.DateTimeField(default=django.utils.timezone.now)

    is_confirmed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    # TODO: ADD LOATION ETC DETAILS FOR THIS CONTRACT.......

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


# Only 'CORPORATE' offer products
class Product(models.Model):
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_by_user_set')

    name = models.CharField(max_length=32, default='')  # product's name
    text = models.TextField(default='')  # description, in detail, of this product
    price = models.IntegerField(default=0)
    photo = models.ImageField(
        upload_to='products_photos/',
        default=''
    )  # MEDIA_ROOT/products_photos/ # TODO: MIGHT BE UNSTABLE IF TWO FILES WITH SAME NAMES ARE UPLOADED

    @property
    def product_photo_url(self):
        if self.photo: return self.photo.url
        else: return '/static/grey.jpg'

    def __str__(self):
        return self.name

# What products brought from company/corporate
class Transaction(models.Model):
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_by_user_set')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_to_user_set')

    text = models.TextField(default='')
    for_contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product) # what products brought per transaction

    is_confirmed = models.BooleanField(default=False)

    @property
    def total_price(self):
        price = 0
        for product in self.products.all():
            price += int(product.price)
        return price

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# If a user gives review/rating to other user.
class Review(models.Model):
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_by_user_set')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_to_user_set')

    is_positive = models.BooleanField(default=False)
    text = models.TextField(default='')
    date = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return self.text


# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# If any two users talk. (only contractors and clients can speak to each other ONLY at contract's page)
class Message(models.Model):
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_by_user_set')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_to_user_set')

    for_contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    text = models.TextField(default='')  # the message
    date = models.DateTimeField(default=django.utils.timezone.now)

    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.by_user.username + ' -> ' + self.to_user.username

