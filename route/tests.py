from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.test import Client
from django.contrib.auth.models import Permission

import route.views
from route.views import add_review, add_route, route_info
from route import models
import datetime
import re


def create_test_review(*args, **kwargs):
    test_review = models.Review(route_review='test', route_rate=100, route_id_id=100)
    test_review.save()
    return test_review.pk


def create_test_route(*args, **kwargs):
    test_route = models.Route(route_type='TEST', departure=1,
                              stopping={'test': 'test'},
                              destination=1, route_name='TEST',
                              country='TEST',
                              location='TEST', description='TEST', duration=1)
    test_route.save()
    return test_route.pk


def create_test_event(route_id):
    date_today = datetime.date.today()
    test_event = models.Event(route_id=route_id,
                              start_date=date_today,
                              price=100,
                              event_admin=1,
                              event_users='')
    test_event.save()
    return test_event.pk


class TestRoute(TestCase):

    def test_discover(self):
        client = Client()
        response = client.get('/route/')
        self.assertEqual(200, response.status_code)

    def test_filter_route_1(self):
        client = Client()
        route_type = 'cycling'
        response = client.get(f'/route/{route_type}/')
        self.assertEqual(200, response.status_code)

    def test_filter_route_2(self):
        client = Client()
        route_type = 'cycling'
        country = 'Ukraine'
        response = client.get(f'/route/{route_type}/{country}/')
        self.assertEqual(200, response.status_code)

    def test_filter_route_3(self):
        client = Client()
        route_type = 'cycling'
        country = 'Ukraine'
        location = 'Lviv'
        response = client.get(f'/route/{route_type}/{country}/{location}/')
        self.assertEqual(200, response.status_code)

    def test_route_info(self):
        client = Client()
        route_id = create_test_route()
        response = client.get(f'/route/{route_id}')
        self.assertEqual(200, response.status_code)

    def test_event(self):
        client = Client()
        route_id = create_test_route()
        response = client.get(f'/route/{route_id}/event')
        self.assertEqual(200, response.status_code)

    def test_event_func(self):
        client = Client()
        route_id = create_test_route()
        response = client.get(f'/route/{route_id}/event')
        self.assertEqual(200, response.status_code)

    def test_event_func_2(self):
        client = Client()
        route_id = create_test_route()
        event_id = create_test_event(route_id)
        response = client.get(f'/route/{route_id}/event/{event_id}')
        self.assertEqual(200, response.status_code)


class TestReview(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test', email='test@gmail.com', password='test')

    def test_review(self):
        client = Client()
        route_id = create_test_route()
        response = client.get(f'/route/{route_id}/review')
        self.assertEqual(200, response.status_code)

    def test_add_review_get_logged_with_perm(self):
        route_id = create_test_route()
        request = self.factory.get(f'/route/{route_id}/add_review')

        # added permission "add_review"
        self.user.user_permissions.add((Permission.objects.get(codename='add_review')))
        request.user = self.user

        response = add_review(request, route_id)
        self.assertEqual(200, response.status_code)

    def test_add_review_post_logged_with_perm(self):
        route_id = create_test_route()
        request = self.factory.post(f'/route/{route_id}/add_review', {'route_review': 'test',
                                                                      'route_rate': 100,
                                                                      'route_id': route_id})
        # added permission
        self.user.user_permissions.add((Permission.objects.get(codename='add_review')))
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)
        # should redirect to review
        self.assertEqual(f'/route/{route_id}/review', response.url)

    def test_add_review_get_not_logged(self):
        client = Client()
        route_id = create_test_route()
        response = client.get(f'/route/{route_id}/add_review')
        # if not logged - redirect to account/login
        self.assertEqual(f'/account/login/?next=/route/{route_id}/add_review', response.url)

    # identical with - test_add_review_get_not_logged
    def test_add_review_post_not_logged(self):
        client = Client()
        route_id = create_test_route()
        response = client.get(f'/route/{route_id}/add_review')
        # if not logged - redirect to account/login
        self.assertEqual(f'/account/login/?next=/route/{route_id}/add_review', response.url)

    def test_add_review_get_logged_with_no_perm(self):
        route_id = create_test_route()
        request = self.factory.get(f'/route/{route_id}/add_review')
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)

        #  redirect to 'route/{route_id}' - when user has no perm
        self.assertEqual(f'/route/{route_id}', response.url)

    def test_add_review_post_logged_with_no_perm(self):
        route_id = create_test_route()
        request = self.factory.post(f'/route/{route_id}/add_review', {'route_review': 'test',
                                                                      'route_rate': 10,
                                                                      'route_id': route_id})
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)
        #  redirect to 'route/{route_id}' - when user has no perm
        self.assertEqual(f'/route/{route_id}', response.url)


# with mock
# perm = True, is_authenticated = True
class TestReview2(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()

        class UserMock:

            def has_perm(self, *args, **kwargs):
                return True

            def is_authenticated(self, *args, **kwargs):
                return True

        self.user = UserMock()

    def test_add_review_get_logged_with_perm_2(self):
        route_id = create_test_route()
        request = self.factory.get(f'/route/{route_id}/add_review')
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)
        self.assertEqual(200, response.status_code)

    def test_add_review_post_logged_with_perm_2(self):
        route_id = create_test_route()
        request = self.factory.post(f'/route/{route_id}/add_review', {'route_review': 'test',
                                                                      'route_rate': 100,
                                                                      'route_id': route_id})
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)
        # if user logged and has perm redirect, after adding review, to route/{route_id}/review
        self.assertEqual(f'/route/{route_id}/review', response.url)


# perm = False, is_authenticated = True
class TestReview3(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()

        class UserMock:

            def has_perm(self, *args, **kwargs):
                return False

            def is_authenticated(self, *args, **kwargs):
                return True

        self.user = UserMock()

    def test_add_review_get_logged_with_no_perm_3(self):
        route_id = create_test_route()
        request = self.factory.get(f'/route/{route_id}/add_review')
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)
        #  redirect to 'route/{route_id}' - when user has no perm
        self.assertEqual(f'/route/{route_id}', response.url)

    def test_add_review_post_logged_with_no_perm_3(self):
        route_id = create_test_route()
        request = self.factory.post(f'/route/{route_id}/add_review', {'route_review': 'test',
                                                                      'route_rate': 10,
                                                                      'route_id': route_id})
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)
        #  redirect to 'route/{route_id}' - when user has no perm
        self.assertEqual(f'/route/{route_id}', response.url)


# fixtures
class TestEventFixture(TestCase):
    fixtures = ['review.json']

    def test_review(self):
        client = Client()
        review = models.Review.objects.get(pk=2)
        response = client.get('/route/2/review')
        self.assertEqual(response.status_code, 200)

        parsed_response = re.search(r'"route_id": "2"', str(response.content)).group(0)
        self.assertEqual('"route_id": "2"', parsed_response)
        self.assertEqual(review.id, int(parsed_response[-2:-1]))


class TestAddReviewFixtures(TestCase):
    fixtures = ['review.json']

    def setUp(self) -> None:
        self.factory = RequestFactory()

        class UserMock:

            def has_perm(self, *args, **kwargs):
                return True

            def is_authenticated(self, *args, **kwargs):
                return True

        self.user = UserMock()

    def test_add_review_get(self):
        route = models.Route.objects.get(pk=1)
        request = self.factory.get(f'/route/{route.id}/add_review')
        request.user = self.user
        response = add_review(request, route.id)
        parsed_response = re.search(r'Please add your review', str(response.content)).group(0)
        self.assertEqual(200, response.status_code)
        self.assertEqual('Please add your review', parsed_response)

    def test_add_review_post(self):
        route = models.Route.objects.get(pk=1)
        data = {'route_id': f'{route.id}', 'route_rate': 99, 'route_review': 'www'}
        request = self.factory.post(f'/route/{route.id}/add_review', data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route.id)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/route/{route.id}/review', response.url)
        added_review = models.Review.objects.filter(route_review=data['route_review']).first()
        self.assertEqual(added_review.route_review, data['route_review'])


class MockCollection:

    def find_one(self, *args, **kwargs):
        return {}


class MongoClientMock:

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def __getitem__(self, item):
        return {'stopping': MockCollection()}


class TestInfoRouteFixtures(TestCase):
    fixtures = ['route.json']

    @patch('utils.mongo_utils.MongoClient', MongoClientMock)
    def test_route_info(self):
        client = Client()
        route = models.Route.objects.get(pk=1)
        response = client.get(f'/route/{route.id}')
        self.assertEqual(200, response.status_code)
        parsed_response = re.search(r'"route_id": "1"', str(response.content)).group(0)
        self.assertEqual(route.id, int(parsed_response[-2:-1]))
