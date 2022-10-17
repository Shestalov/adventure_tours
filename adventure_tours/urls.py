from django.contrib import admin
from django.urls import path, include
from route import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('route/', include('route.urls')),
    path('account/', include('account.urls'))
]
