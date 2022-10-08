from django.shortcuts import render, redirect
from . import models
import datetime
from django.contrib.auth.decorators import login_required


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

    if result.exists():
        return render(request, 'route/filter_route.html', {'result': result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Does not exist'})


def route_info(request, route_id):
    result = models.Route.objects.filter(pk=route_id)
    if result.exists():
        future_events = result[0].event_set.filter(start_date__gte=datetime.date.today())
        return render(request, 'route/route_info.html', {'result': result, 'future_events': future_events})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Route does not exist'})


def review(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    if result.exists():
        return render(request, 'route/review.html', {'result': result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Reviews do not exist'})


def event(request, route_id):
    result = models.Event.objects.all().filter(route_id=route_id, start_date__gte=datetime.date.today())
    if result.exists():
        return render(request, 'route/event.html', {"result": result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Events do not exist'})


@login_required(login_url='account:login')
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
        route_name = request.POST.get('route_name')

        departure_obj = models.Place.objects.get(name=departure)
        destination_obj = models.Place.objects.get(name=destination)

        new_route = models.Route(route_type=route_type, departure=departure_obj.id, stopping={'test': 'test'},
                                 destination=destination_obj.id, route_name=route_name, country=country,
                                 location=location, description=description, duration=duration)
        new_route.save()
        return redirect('home')


# @login_required(login_url='account:login')
def add_event(request, route_id):
    if request.user.has_perm('route.add_event'):
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
    else:
        return redirect('account:login')


@login_required(login_url='account:login')
def add_review(request, route_id):
    if request.method == 'GET':
        return render(request, 'route/add_review.html')
    if request.method == 'POST':
        route_id = route_id
        route_review = request.POST.get('route_review')
        route_rate = request.POST.get('route_rate')
        new_event = models.Review(route_review=route_review, route_rate=route_rate, route_id_id=route_id)
        new_event.save()
        return redirect('home')
