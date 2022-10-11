from django.urls import path
from . import views

app_name = 'route'

urlpatterns = [
    path('', views.discover, name='discover'),
    path('<str:route_type>/', views.filter_route, name='route_type'),
    path('<str:route_type>/<str:country>/', views.filter_route, name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>/', views.filter_route, name='route_location'),

    path('add_route', views.add_route, name='add_route'),
    path('<int:route_id>', views.route_info, name='info'),
    path('<int:route_id>/event', views.event, name='event'),
    path('<int:route_id>/review', views.review, name='review'),
    path('<int:route_id>/add_review', views.add_review, name='add_review'),
    path('<int:route_id>/add_event', views.add_event, name='add_event')
]
