from django.contrib import admin

# No models to register yet - payments are handled by Stripe
# Premium status is stored in User model

admin.site.site_header = "NewsDebate Admin"
admin.site.site_title = "NewsDebate Admin Portal"
admin.site.index_title = "Welcome to NewsDebate Admin"