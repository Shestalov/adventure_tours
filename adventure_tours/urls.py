from django.contrib import admin
from django.urls import path, include
from route import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('route/', include('route.urls')),
    path("event/<event_id>", views.event_handler)
]
