from django.db import models
from django.contrib import admin
# Create your models here.
from django.db import models


class HarmfulIngredient(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class ProductRating(models.Model):
    product_name = models.CharField(max_length=255)
    ingredients = models.TextField()  # This will store the text retrieved from OCR
    rating = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product_name} - Rating: {self.rating}'

