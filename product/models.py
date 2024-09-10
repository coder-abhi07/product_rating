# # from django.db import models
# # from django.contrib import admin
# # # Create your models here.
# # from django.db import models


# # # class HarmfulIngredient(models.Model):
# # #     name = models.CharField(max_length=255, unique=True)

# # #     def __str__(self):
# # #         return self.name

# # # class ProductRating(models.Model):
# # #     product_name = models.CharField(max_length=255)
# # #     ingredients = models.TextField()  # This will store the text retrieved from OCR
# # #     rating = models.DecimalField(max_digits=5, decimal_places=2)
# # #     created_at = models.DateTimeField(auto_now_add=True)

# # #     def __str__(self):
# # #         return f'{self.product_name} - Rating: {self.rating}'



# # from django.db import models
# # from django.contrib.auth.models import User

# # class HarmfulIngredient(models.Model):
# #     name = models.CharField(max_length=255, unique=True)
# #     description = models.TextField(null=True, blank=True)
# #     average_rating = models.FloatField(default=0)

# #     def __str__(self):
# #         return self.name

# #     def update_average_rating(self):
# #         reviews = self.reviews.all()
# #         if reviews:
# #             avg = sum([review.rating for review in reviews]) / len(reviews)
# #             self.average_rating = avg
# #             self.save()

# # class IngredientReview(models.Model):
# #     ingredient = models.ForeignKey(HarmfulIngredient, on_delete=models.CASCADE, related_name='reviews')
# #     user = models.ForeignKey(User, on_delete=models.CASCADE)
# #     rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
# #     review_text = models.TextField()
# #     created_at = models.DateTimeField(auto_now_add=True)

# #     class Meta:
# #         unique_together = ('ingredient', 'user')  # Prevent duplicate reviews by the same user for the same ingredient

# # class ProductRating(models.Model):
# #     product_name = models.CharField(max_length=255)
# #     ingredients = models.TextField()  # This will store the text retrieved from OCR
# #     rating = models.DecimalField(max_digits=5, decimal_places=2)  # Ensure this matches your data
# #     created_at = models.DateTimeField(auto_now_add=True)

# #     def __str__(self):
# #         return f'{self.product_name} - Rating: {self.rating}'

# # from django import forms
# # from .models import IngredientReview

# # class IngredientReviewForm(forms.ModelForm):
# #     class Meta:
# #         model = IngredientReview
# #         fields = ['rating', 'review_text']
# #         widgets = {
# #             'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
# #             'review_text': forms.Textarea(attrs={'rows': 4}),
# #         }



# from django.db import models
# from django.contrib.auth.models import User
# from django.db.models import Avg

# class Ingredient(models.Model):
#     name = models.CharField(max_length=255)
#     harmful = models.BooleanField(default=False)

#     def __str__(self):
#         return self.name
# class HarmfulIngredient(models.Model):
#     name = models.CharField(max_length=255)
#     harmful = models.BooleanField(default=True)
    
#     def update_average_rating(self):
#         reviews = IngredientReview.objects.filter(ingredient=self)
#         average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
#         self.average_rating = average_rating
#         self.save()

# class IngredientReview(models.Model):
#     ingredient = models.ForeignKey(HarmfulIngredient, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     rating = models.PositiveIntegerField()
#     review_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

# # models.py
# from django.db import models

# class ProductRating(models.Model):
#     product_name = models.CharField(max_length=255)
#     ingredients = models.TextField() 
#     rating = models.IntegerField() 

# # models.py
# from django.db import models
# from django.contrib.auth.models import User

# class ProductRating(models.Model):
#     product_name = models.CharField(max_length=255)
#     rating = models.IntegerField()
#     ingredients = models.TextField()

# class Review(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(ProductRating, on_delete=models.CASCADE)
#     review_text = models.TextField()
#     approved = models.BooleanField(default=False)  # Only approved reviews will be visible


# models.py
from django.db import models
from django.contrib.auth.models import User

class HarmfulIngredient(models.Model):
    name = models.CharField(max_length=255)
    harmful = models.BooleanField(default=True)
    
    def update_average_rating(self):
        reviews = IngredientReview.objects.filter(ingredient=self, approved=True)  # Only count approved reviews
        average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        self.average_rating = average_rating
        self.save()

class IngredientReview(models.Model):
    ingredient = models.ForeignKey(HarmfulIngredient, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
    review_text = models.TextField()
    approved = models.BooleanField(default=False)  # Requires admin approval
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ingredient', 'user')  # Prevent duplicate reviews by the same user for the same ingredient


# product/models.py
from django.db import models

class ProductRating(models.Model):
    product_name = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=5, decimal_places=2)
    review = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ingredients = models.TextField() 

    def __str__(self):
        return f"{self.product_name} - {self.rating}"



