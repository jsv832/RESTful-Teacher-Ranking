"""
URL configuration for djangodb project.
"""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    # Default admin site
    path('admin/', admin.site.urls),        
    # URLs from app    
    path('api/', include('website.urls')),      
]

