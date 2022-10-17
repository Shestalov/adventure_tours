from django.shortcuts import render, redirect
from . import models
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from .forms import AddReviewForm
from utils.mongo_utils import MongoDBConnection
from bson import ObjectId


def discover(request):
    if request.method == 'GET':
        uniq_routes_type = models.Route.objects.values('route_type').distinct()
        return render(request, 'route/discover.html', {'route_type': uniq_routes_type})
    if request.method == 'POST':
        route_type = request.POST.get('route_type')
        country = request.POST.get('country')
        return filter_route(request, route_type=route_type, country=country)


def filter_route(request, route_type=None, country=None, location=None):
    cursor = connection.cursor()
    query_filter = []

    if route_type is not None:
        query_filter.append(f"route_type='{route_type}'")
    if country is not None:
        query_filter.append(f"country='{country}'")
    if location is not None:
        query_filter.append(f"location='{location}'")

    filter_string = ' and '.join(query_filter)

    joining = """SELECT route_route.route_name, 
                        route_route.route_type, 
                        route_route.country, 
                        route_route.location, 
                        start.name  AS departure, 
                        finish.name AS destination,
                        route_route.description, 
                        route_route.duration, 
                        route_route.id
                    FROM route_route 
                    JOIN route_place as start 
                    ON start.id = route_route.departure 
                    JOIN route_place as finish 
                    ON finish.id = route_route.destination 
                    WHERE """ + filter_string + """ORDER BY route_route.id DESC"""

    cursor.execute(joining)
    result_joining = cursor.fetchall()
    result = [{'route_name': itm[0], 'route_type': itm[1], 'country': itm[2], 'location': itm[3], 'departure': itm[4],
               'destination': itm[5], 'description': itm[6], 'duration': itm[7], 'route_id': itm[8]} for itm in
              result_joining]

    return render(request, 'route/filter_route.html', {'result': result})


def route_info(request, route_id):
    cursor = connection.cursor()

    raw_query_route = f"""SELECT route_route.route_name,
                            route_route.route_type,
                            route_route.country,
                            route_route.location,
                            route_route.description,
                            route_route.duration,
                            start.name                     AS departure,
                            route_route.stopping,
                            finish.name                    AS destination
                            FROM route_route
                                     JOIN route_place AS start
                                          ON start.id = route_route.departure
                                     JOIN route_place AS finish
                                          ON finish.id = route_route.destination
                            WHERE route_route.id = '{route_id}';"""

    events = models.Event.objects.filter(route_id=route_id).all()
    reviews = models.Review.objects.filter(route_id_id=route_id).all()

    cursor.execute(raw_query_route)
    row = cursor.fetchall()
    result = [{'route_name': itm[0], 'route_type': itm[1], 'country': itm[2], 'location': itm[3],
               'description': itm[4], 'duration': itm[5], 'departure': itm[6], 'stopping': itm[7],
               'destination': itm[8], 'route_id': route_id} for itm in row]

    if result:
        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            collection = db['stopping']
            stopping = collection.find_one({'_id': ObjectId(result[0]['stopping'])})
    else:
        stopping = None

    return render(request, 'route/route_info.html',
                  {'result': result, 'stopping': stopping, 'event': events, 'review': reviews})


def review(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    if result.exists():
        return render(request, 'route/review.html', {'result': result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Reviews do not exist (View)'})


def event(request, route_id):
    cursor = connection.cursor()
    raw_query = f"""SELECT route_route.route_type, 
                            route_event.event_admin,
                            route_event.start_date, 
                            route_event.price, 
                            route_route.country, 
                            route_route.location,
                            start.name  AS departure, 
                            route_route.stopping,
                            finish.name AS destination,
                            route_route.duration, 
                            route_route.route_name
                            FROM route_event
                                 JOIN route_route
                                      ON route_event.route_id = route_route.id
                                 JOIN route_place as start
                                      ON start.id = route_route.departure
                                 JOIN route_place AS finish
                                      ON finish.id = route_route.destination
                            WHERE route_id='{route_id}' AND route_event.start_date >= '{datetime.date.today()}';"""

    cursor.execute(raw_query)
    row = cursor.fetchall()

    result = [{'route_type': itm[0], 'event_admin': itm[1], 'start_date': itm[2],
               'price': itm[3], 'country': itm[4], 'location': itm[5], 'departure': itm[6],
               'stopping': itm[7], 'destination': itm[8], 'duration': itm[9], 'route_name': itm[10]} for itm in row]

    if result:
        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            collection = db['stopping']
            stopping = collection.find_one({'_id': ObjectId(result[0]['stopping'])})
    else:
        stopping = None

    return render(request, 'route/event.html', {'result': result, 'stopping': stopping})


@login_required(login_url='account:login')
def add_route(request):
    if request.user.has_perm('route.add_route'):
        if request.method == 'GET':
            uniq_routes_type = models.Route.objects.values('route_type').distinct()
            return render(request, 'route/add_route.html', {'route_type': uniq_routes_type})

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

            new_route = models.Route.objects.create(route_type=route_type, departure=departure_obj.id,
                                                    stopping={'test': 'test'},
                                                    destination=destination_obj.id, route_name=route_name,
                                                    country=country,
                                                    location=location, description=description, duration=duration)
            new_route.save()
            messages.success(request, "Route was added")
            return redirect(new_route)
    else:
        messages.error(request, "User does not have permission!")
        return redirect('home')


@login_required(login_url='account:login')
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
            messages.success(request, "Event was added")
            return redirect('home')
    else:
        messages.error(request, "User does not have permission!")
        return redirect('home')


@login_required(login_url='account:login')
def add_review(request, route_id):
    if request.user.has_perm('route.add_review'):
        if request.method == 'GET':
            return render(request, 'route/add_review.html')
        if request.method == 'POST':
            route_id = route_id
            route_review = request.POST.get('route_review')
            route_rate = request.POST.get('route_rate')
            new_event = models.Review(route_review=route_review, route_rate=route_rate, route_id_id=route_id)
            new_event.save()
            messages.success(request, "Review was added")
            return redirect('home')
    else:
        messages.error(request, "User does not have permission!")
        return redirect('home')


@login_required(login_url='account:login')
def test_page(request):
    if request.user.has_perm('route.add_review'):
        if request.method == 'POST':
            form = AddReviewForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Review was added")
                return redirect('home')
        else:
            form = AddReviewForm()
        return render(request, 'route/test_page.html', {'form': form})
    else:
        messages.error(request, "User does not have permission!")
        return redirect('home')
