from django.contrib import admin
from django.urls import path, include 
from django.views.generic.base import RedirectView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/problems/', permanent=True)),
    path('api/users/', include('apps.users.urls')),
    path('problems/', include('apps.problems.urls')),
]
