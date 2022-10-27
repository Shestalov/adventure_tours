import json
import datetime
from . import models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from .forms import AddReviewForm
from utils.mongo_utils import MongoDBConnection
from bson import ObjectId
from django.contrib.auth.models import User
import os
from utils.validations import validation_stopping, validation_route_type, validation_date
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator


def discover(request):
    if request.method == 'GET':
        uniq_routes_type = models.Route.objects.values('route_type').distinct()
        return render(request, 'route/discover.html', {'route_type': uniq_routes_type})
    if request.method == 'POST':
        route_type = request.POST.get('route_type')
        country = request.POST.get('country')

        return redirect('route:route_country', route_type=route_type, country=country)


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
    result = [{'route_name': itm[0], 'route_type': itm[1], 'country': itm[2],
               'location': itm[3], 'departure': itm[4], 'destination': itm[5],
               'description': itm[6], 'duration': itm[7], 'route_id': itm[8]} for itm in result_joining]

    #  paginator
    paginator = Paginator(result, 3)
    page_number = int(request.GET.get('page', default=1))
    if page_number > paginator.num_pages:
        page_number = 1

    page_obj = paginator.get_page(page_number)
    previous_page = page_obj.previous_page_number() if page_number > 1 else 1
    next_page = page_obj.next_page_number() if page_number < paginator.num_pages else paginator.num_pages
    all_pages = paginator.num_pages

    return render(request, 'route/filter_route.html', {'page_obj': page_obj.object_list,
                                                       'previous_page': previous_page,
                                                       'next_page': next_page,
                                                       'current_page': page_number,
                                                       'all_pages': all_pages})


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

    events = models.Event.objects.filter(route_id=route_id, start_date__gte=datetime.date.today()).all()
    reviews = models.Review.objects.filter(route_id_id=route_id).all()

    cursor.execute(raw_query_route)
    row = cursor.fetchall()
    result = [{'route_name': itm[0], 'route_type': itm[1], 'country': itm[2], 'location': itm[3],
               'description': itm[4], 'duration': itm[5], 'departure': itm[6], 'stopping': itm[7],
               'destination': itm[8], 'route_id': route_id} for itm in row]

    if result:
        with MongoDBConnection(os.environ['MONGO_PASSWORD'], os.environ['MONGO_USERNAME'], os.environ['MONGO_HOST'],
                               os.environ['MONGO_PORT']) as db:
            collection = db['stopping']
            stopping = collection.find_one({'_id': ObjectId(result[0]['stopping'])})
    else:
        stopping = None

    return render(request, 'route/route_info.html',
                  {'result': result, 'stopping': stopping, 'event': events, 'review': reviews})


def review(request, route_id):
    result = models.Review.objects.filter(route_id=route_id).select_related('route_id').all()
    if result.exists():
        return render(request, 'route/review.html', {'result': result})
    else:
        return render(request, 'route/does_not_exist.html', {'result': 'Reviews do not exist (msg from views)'})


def event(request, route_id, event_id=None):
    if event_id is None:
        return render(request, 'route/event.html', event_func(request, route_id))
    else:

        # checking for button in template event_info
        data = event_func(request, route_id, event_id)

        button = False
        if len(data['result']) > 0:

            pending = data['result'][0]['pending']
            accepted = data['result'][0]['accepted']

            for itm in accepted:
                if request.user.id in itm:
                    button = True

            for itm in pending:
                if request.user.id in itm:
                    button = True

        return render(request, 'route/event_info.html',
                      {'result': event_func(request, route_id, event_id), 'button': button})


def event_func(request, route_id, event_id=None):
    cursor = connection.cursor()
    query_filter = []

    if route_id is not None:
        query_filter.append(f"route_id='{route_id}'")
    if event_id is not None:
        query_filter.append(f"route_event.id='{event_id}'")

    filter_string = ' and '.join(query_filter)

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
                            route_route.route_name,
                            route_event.event_users,
                            route_event.id,
                            route_route.id
                            FROM route_event
                                 JOIN route_route
                                      ON route_event.route_id = route_route.id
                                 JOIN route_place as start
                                      ON start.id = route_route.departure
                                 JOIN route_place AS finish
                                      ON finish.id = route_route.destination
                            WHERE """ + filter_string + \
                f"""AND route_event.start_date >= '{datetime.date.today()}' ORDER BY route_event.id DESC;"""

    cursor.execute(raw_query)
    row = cursor.fetchall()

    result = [{'route_type': itm[0],
               'event_admin': itm[1],
               'start_date': itm[2],
               'price': itm[3],
               'country': itm[4],
               'location': itm[5],
               'departure': itm[6],
               'stopping': itm[7],
               'destination': itm[8],
               'duration': itm[9],
               'route_name': itm[10],
               'event_users_id': itm[11],
               'event_id': itm[12],
               'route_id': itm[13]} for itm in row]

    if result:
        with MongoDBConnection(os.environ['MONGO_PASSWORD'], os.environ['MONGO_USERNAME'], os.environ['MONGO_HOST'],
                               os.environ['MONGO_PORT']) as db:
            collection_stopping = db['stopping']
            stopping = collection_stopping.find_one({'_id': ObjectId(result[0]['stopping'])})

            if request.user.id == result[0]['event_admin']:
                pass

            for num in range(len(result)):
                if result[num]['event_users_id'] != '':
                    collection_users = db['event_users']
                    users = collection_users.find_one({'_id': ObjectId(result[num]['event_users_id'])})

                    user_accepted = User.objects.filter(pk__in=users['accepted'])
                    user_pending = User.objects.filter(pk__in=users['pending'])

                    list_user_accepted = [{itm.id: itm.username} for itm in user_accepted]
                    list_user_pending = [{itm.id: itm.username} for itm in user_pending]

                    result[num]['accepted'] = list_user_accepted
                    result[num]['pending'] = list_user_pending
    else:
        stopping = None

    return {'result': result, 'stopping': stopping}


@login_required(login_url='account:login')
def add_me_to_event(request, route_id, event_id):
    user = request.user.id
    event_ = models.Event.objects.filter(id=event_id, route_id=route_id).first()

    # checking if user is admin of event. Admin can not be in accepting or pending!
    if request.user.id == event_.event_admin:
        messages.error(request, 'You are admin of event!')
        return redirect('route:event_info', route_id=route_id, event_id=event_id)
    else:
        with MongoDBConnection(os.environ['MONGO_PASSWORD'], os.environ['MONGO_USERNAME'], os.environ['MONGO_HOST'],
                               os.environ['MONGO_PORT']) as db:
            collection_event_users = db['event_users']
            # when new event is created the 'route_event.event_users' cell will be empty
            # checking if any users joined to event or not
            if event_.event_users != '':
                event_users = collection_event_users.find_one({'_id': ObjectId(event_.event_users)})

                # checking if user in pending or in accepted
                # the event_admin can not be in pending or accepted
                if user in event_users['pending'] or user in event_users['accepted']:
                    messages.error(request, 'Your are already joined to event!')
                else:
                    event_users['pending'].append(user)
                    collection_event_users.update_one({'_id': ObjectId(event_.event_users)},
                                                      {'$set': event_users}, upsert=False)
                    messages.success(request, 'You are joined to event!')
            else:
                # added user in new line (mongo)
                new_user = collection_event_users.insert_one({"accepted": [], "pending": [user]})
                # put id(from mongo) in route_event(to sqlite)
                event_.event_users = new_user.inserted_id
                event_.save()
                messages.success(request, 'You are joined to event!')

        return redirect('route:event_info', route_id=route_id, event_id=event_id)


@login_required(login_url='account:login')
def users_of_event(request, route_id, event_id):
    event_ = models.Event.objects.all().filter(id=event_id).select_related('route').first()

    if (event_ is not None) and request.user.id == event_.event_admin:

        with MongoDBConnection(os.environ['MONGO_PASSWORD'], os.environ['MONGO_USERNAME'], os.environ['MONGO_HOST'],
                               os.environ['MONGO_PORT']) as db:
            collection_users = db['event_users']

            if event_.event_users is not '':
                users = collection_users.find_one({'_id': ObjectId(event_.event_users)})
            else:
                users = None

            if request.method == 'GET':
                return render(request, 'route/users_of_event.html', {'event': event_, 'users': users})

            if request.method == 'POST':
                pending_user = int(request.POST.get('user_id'))

                users['pending'].pop(users['pending'].index(pending_user))
                users['accepted'].append(pending_user)

                collection_users.update_one({'_id': ObjectId(event_.event_users)}, {'$set': users}, upsert=False)

                messages.success(request, f'User id: {pending_user}'
                                          f' username:(not yet added) was added to accepted users')
                return redirect('route:event_users', route_id=route_id, event_id=event_id)
    else:
        messages.error(request, 'You are not admin of event')
        return redirect('route:event_info', route_id=route_id, event_id=event_id)


@login_required(login_url='account:login')
def add_route(request):
    if request.user.has_perm('route.add_route'):
        if request.method == 'GET':
            uniq_routes_type = models.Route.objects.values('route_type').distinct()
            return render(request, 'route/add_route.html', {'route_type': uniq_routes_type})

        if request.method == 'POST':
            route_type = request.POST.get('route_type')
            departure = request.POST.get('departure')
            stopping = request.POST.get('stopping')
            destination = request.POST.get('destination')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            route_name = request.POST.get('route_name')

            departure_obj = models.Place.objects.get(name=departure)
            destination_obj = models.Place.objects.get(name=destination)

            try:
                validation_stopping(stopping)
                validation_route_type(route_type)
            except (ValidationError, BaseException) as error:
                messages.error(request, error.message)
                return redirect('route:add_route')

            stopping_list = json.loads(stopping)

            with MongoDBConnection(os.environ['MONGO_PASSWORD'], os.environ['MONGO_USERNAME'], os.environ['MONGO_HOST'],
                                   os.environ['MONGO_PORT']) as db:
                collection = db['stopping']
                stopping_id = collection.insert_one({'points': stopping_list}).inserted_id

            new_route = models.Route.objects.create(route_type=route_type, departure=departure_obj.id,
                                                    stopping=stopping_id,
                                                    destination=destination_obj.id, route_name=route_name,
                                                    country=country,
                                                    location=location, description=description, duration=duration)

            new_route.full_clean()
            new_route.save()

            messages.success(request, "Route was added")
            return redirect("route:route_info", route_id=new_route.pk)
    else:
        messages.error(request, "User does not have permission!")
        return redirect('main:home')


@login_required(login_url='account:login')
def add_event(request, route_id):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'route/add_event.html')

        if request.method == 'POST':
            route_id = route_id
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')

            try:
                validation_date(start_date)
            except ValidationError as error:
                messages.error(request, error.message)
                return redirect('route:add_event', route_id=route_id)

            with MongoDBConnection(os.environ['MONGO_PASSWORD'], os.environ['MONGO_USERNAME'], os.environ['MONGO_HOST'],
                                   os.environ['MONGO_PORT']) as db:
                collection_event_users = db['event_users']
                new_users = collection_event_users.insert_one({'accepted': [], 'pending': []})

                new_event = models.Event(route_id=route_id,
                                         start_date=start_date,
                                         price=price,
                                         event_admin=request.user.id,
                                         event_users=new_users.inserted_id)

            new_event.full_clean()
            new_event.save()

            messages.success(request, 'Event was added')
            return redirect('route:event_info', route_id=route_id, event_id=new_event.pk)
    else:
        messages.error(request, 'User does not have permission!')
        return redirect('route:route_info', route_id=route_id)


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
            return redirect('route:review', route_id=route_id)
    else:
        messages.error(request, "User does not have permission!")
        return redirect('route:route_info', route_id=route_id)
