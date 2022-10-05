from django.shortcuts import render, redirect
from . import models
import datetime


# temporary, main page adventure tours
def index(request):
    return render(request, 'route/index.html')


def filter_route(request, route_type=None, country=None, location=None):
    query_filter = {}

    if route_type is not None:
        query_filter['route_type'] = route_type
    if country is not None:
        query_filter['country'] = country
    if location is not None:
        query_filter['location'] = location

    result = models.Route.objects.all().filter(**query_filter)
    return render(request, 'route/filter_route.html', {'result': result})


def info(request, route_id):
    result = models.Route.objects.filter(pk=route_id)
    future_events = result[0].event_set.filter(start_date__gte=datetime.date.today())
    return render(request, 'route/info.html', {'result': result, 'future_events': future_events})


def review(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    return render(request, 'route/review.html', {'result': result})


def add_route(request):
    if request.method == 'GET':
        return render(request, 'route/add_route.html')

    if request.method == 'POST':
        route_type = request.POST.get('route_type')
        departure = request.POST.get('departure')
        destination = request.POST.get('destination')
        country = request.POST.get('country')
        location = request.POST.get('location')
        description = request.POST.get('description')
        duration = request.POST.get('duration')

        departure_obj = models.Place.objects.get(name=departure)
        destination_obj = models.Place.objects.get(name=destination)

        new_route = models.Route(route_type=route_type, departure=departure_obj.id, stopping={'test': 'test'},
                                 destination=destination_obj.id,
                                 country=country, location=location, description=description, duration=duration)
        new_route.save()
        return redirect('home')


def add_event(request, route_id):
    if request.method == 'GET':
        return render(request, 'route/add_event.html')
    if request.method == 'POST':
        route_id = route_id  # request.POST.get('route_id')
        start_date = request.POST.get('start_date')
        price = request.POST.get('price')
        new_event = models.Event(route_id=route_id, start_date=start_date, price=price, event_admin=1,
                                 approved_users={'test': 'test'}, pending_users={'test': 'test'})
        new_event.save()
        return redirect('home')


def event(request, route_id):
    result = models.Event.objects.all().filter(route_id=route_id)
    return render(request, 'route/event.html', {"result": result})


def login(request):
    pass


def logout(request):
    pass
