from django.db import models
from django.contrib.auth.models import User

# HarmfulIngredient model
class HarmfulIngredient(models.Model):
    name = models.CharField(max_length=255)
    harmful = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_average_rating(self):
        # Only count approved reviews
        reviews = IngredientReview.objects.filter(ingredient=self, approved=True)
        average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        self.average_rating = average_rating
        self.save()

# IngredientReview model
class IngredientReview(models.Model):
    ingredient = models.ForeignKey(HarmfulIngredient, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
    review_text = models.TextField()
    approved = models.BooleanField(default=False)  # Requires admin approval
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate reviews by the same user for the same ingredient
        unique_together = ('ingredient', 'user')


# ProductRating model
class ProductRating(models.Model):
    product_name = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=5, decimal_places=2)
    review = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ingredients = models.TextField()

    def __str__(self):
        return f"{self.product_name} - {self.rating}"
