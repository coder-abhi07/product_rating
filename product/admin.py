# from django.contrib import admin
# from .models import HarmfulIngredient, IngredientReview

# @admin.register(IngredientReview)
# class IngredientReviewAdmin(admin.ModelAdmin):
#     list_display = ('ingredient', 'user', 'rating', 'review_text', 'created_at',)  # Display the 'name' field in the list view


# @admin.register(HarmfulIngredient)
# class HarmfulIngredientAdmin(admin.ModelAdmin):
#     list_display = ('name',)  # Display the 'name' field in the list view


# # admin.py
# from django.contrib import admin
# from .models import ProductRating, Review

# @admin.register(ProductRating)
# class ProductRatingAdmin(admin.ModelAdmin):
#     list_display = ('product_name', 'rating', 'ingredients')  # Customize fields as needed
#     search_fields = ('product_name',)

# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ('user', 'product', 'review_text', 'approved')
#     list_filter = ('approved',)
#     search_fields = ('user__username', 'product__name')
#     actions = ['approve_reviews', 'disapprove_reviews']

#     def approve_reviews(self, request, queryset):
#         queryset.update(approved=True)
#     approve_reviews.short_description = 'Approve selected reviews'

#     def disapprove_reviews(self, request, queryset):
#         queryset.update(approved=False)
#     disapprove_reviews.short_description = 'Disapprove selected reviews'



# admin.py
from django.contrib import admin
from .models import HarmfulIngredient, IngredientReview

class IngredientReviewAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'user', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('ingredient__name', 'user__username', 'review_text')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
        for review in queryset:
            review.ingredient.update_average_rating()
        self.message_user(request, "Selected reviews have been approved.")

    approve_reviews.short_description = 'Approve selected reviews'

admin.site.register(HarmfulIngredient)
admin.site.register(IngredientReview, IngredientReviewAdmin)
