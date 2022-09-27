from django.urls import path
from . import views

app_name = 'route'

urlpatterns = [
    path('', views.filter_route, name='index'),
    path('add_route', views.add_route, name='add_route'),
    path('<int:id_route>', views.detail_route, name='route_detail'),
    path('<int:id_route>/review', views.review_route, name='review_route'),
    path('<int:id_route>/add_event', views.add_event_route, name='add_event_route'),

    path('<str:route_type>', views.filter_route, name='route_type'),
    path('<str:route_type>/<str:country>', views.filter_route, name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.filter_route, name='route_location'),
]