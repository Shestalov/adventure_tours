from django.contrib import admin
from django.urls import path, include
from route import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('route/', include('route.urls'))
]
