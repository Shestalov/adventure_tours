from django.shortcuts import render, redirect
from . import models
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection


# temporary, main page adventure tours
def index(request):
    return render(request, 'route/index.html')


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

    joining = """SELECT route_route.route_name, route_route.route_type, 
                        route_route.country, route_route.location,
                        route_route.departure, route_route.destination, 
                        route_route.description, route_route.duration
                    FROM route_route 
                    JOIN route_place as start 
                    ON start.id = route_route.departure 
                    JOIN route_place as finish 
                    ON finish.id = route_route.destination 
                    WHERE """ + filter_string

    cursor.execute(joining)
    result_joining = cursor.fetchall()
    result = [{'route_name': itm[0], 'route_type': itm[1], 'country': itm[2], 'location': itm[3], 'departure': itm[4],
               'destination': itm[5], 'description': itm[6], 'duration': itm[7]} for itm in result_joining]

    if result is not None:
        return render(request, 'route/filter_route.html', {'result': result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Does not exist'})


def route_info(request, route_id):
    # foreignkey
    # result = models.Route.objects.filter(pk=route_id)

    # raw query
    cursor = connection.cursor()
    raw_query = f"""SELECT route_route.route_name,
                            route_route.route_type,
                            route_route.country,
                            route_route.location,
                            route_route.description,
                            route_route.duration,
                            start.name                     AS departure,
                            finish.name                    AS destination,
                            ROUND(AVG(rate.route_rate), 0) AS avg_rate,
                            COUNT(route_event.start_date)/3  AS events
                            FROM route_route
                                     JOIN route_place AS start
                                          ON start.id = route_route.departure
                                     JOIN route_place AS finish
                                          ON finish.id = route_route.destination
                                     JOIN route_review AS rate
                                          ON rate.route_id_id = route_route.id
                                     JOIN route_event
                                          ON route_event.route_id = route_route.id
                            WHERE route_route.id = '{route_id}'
                              AND route_event.start_date >= '{datetime.date.today()}';"""

    cursor.execute(raw_query)
    row = cursor.fetchall()
    result = [{'route_name': itm[0], 'route_type': itm[1], 'country': itm[2], 'location': itm[3],
               'description': itm[4], 'duration': itm[5], 'departure': itm[6], 'destination': itm[7],
               'avg_rate': itm[8], 'events': itm[9]} for itm in row]

    # if raw query use - if result is not None:
    # if django orm - if result.exists():
    # AND comment/uncomment template
    # + , 'future_events': future_events} to result dict
    if result is not None:
        # future_events = result[0].event_set.filter(start_date__gte=datetime.date.today())
        return render(request, 'route/route_info.html', {'result': result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Route does not exist'})


def review(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    if result.exists():
        return render(request, 'route/review.html', {'result': result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Reviews do not exist'})


def event(request, route_id):
    # foreignkey
    # result = models.Event.objects.all().filter(route_id=route_id, start_date__gte=datetime.date.today())

    # raw query
    cursor = connection.cursor()
    raw_query = f"""SELECT route_route.route_type, route_event.event_admin, route_event.approved_users,
                            route_event.start_date, route_event.price, 
                            route_route.country, route_route.location,
                            route_route.departure, route_route.destination,
                            route_route.duration, route_route.route_name
                            FROM route_event JOIN route_route
                            ON route_event.route_id = route_route.id 
                            WHERE route_id='{route_id}' AND route_event.start_date >= '{datetime.date.today()}';"""

    cursor.execute(raw_query)
    row = cursor.fetchall()

    result = [{'route_type': itm[0], 'event_admin': itm[1], 'approved_users': itm[2], 'start_date': itm[3],
               'price': itm[4], 'country': itm[5], 'location': itm[6], 'departure': itm[7],
               'destination': itm[8], 'duration': itm[9], 'route_name': itm[10]} for itm in row]

    # if raw query use - if result is not None:
    # if django orm - if result.exists():
    # AND comment/uncomment template
    if result is not None:
        return render(request, 'route/event.html', {"result": result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Events do not exist'})


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

            new_route = models.Route(route_type=route_type, departure=departure_obj.id, stopping={'test': 'test'},
                                     destination=destination_obj.id, route_name=route_name, country=country,
                                     location=location, description=description, duration=duration)
            new_route.save()
            messages.success(request, "Route was added")
            return redirect('home')
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
