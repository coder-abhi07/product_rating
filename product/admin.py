from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Customize the admin site's titles
admin.site.site_header = _("Administration")
admin.site.site_title = _("Administration")
admin.site.index_title = _("Welcome to the Admin Dashboard")

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
