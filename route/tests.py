from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.test import Client
from django.contrib.auth.models import Permission

import route.views
from route.views import add_review, add_route
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
        review = models.Review.objects.get(pk=2)
        self.assertEqual(8, review.route_rate)

    def test_review_2(self):
        response = self.client.get('/route/1/review', {'route_id': 1})
        parsed_response = re.search(r'"route_id": "1"', str(response.content)).group(0)
        self.assertEqual('"route_id": "1"', parsed_response)


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
        request = self.factory.get('/route/1/add_review', {'route_id': 1})
        request.user = self.user
        response = add_review(request, 1)
        self.assertEqual(200, response.status_code)

    def test_add_review_post(self):
        route_id = 1
        request = self.factory.post(f'/route/{route_id}/add_review', {'route_id': 1,
                                                                      'route_rate': 99,
                                                                      'route_review': 'aaa'})
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_review(request, route_id)
        self.assertEqual(302, response.status_code)


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


class TestAddRouteFixtures(TestCase):
    fixtures = ['route.json']

    def setUp(self) -> None:
        self.factory = RequestFactory()

        class UserMock:

            def has_perm(self, *args, **kwargs):
                return True

            def is_authenticated(self, *args, **kwargs):
                return True

        self.user = UserMock()

    @patch('utils.mongo_utils.MongoClient', MongoClientMock)
    def test_add_review_2(self):
        request = self.factory.post('/route/add_route', {'route_type': 'hiking',
                                                         'departure': 'Lviv',
                                                         'stopping': '',
                                                         'destination': 'Lviv',
                                                         'route_name': 'test',
                                                         'country': 'Ukraine',
                                                         'location': 'Lviv',
                                                         'description': 'test',
                                                         'duration': 1})
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = add_route(request)
        self.assertEqual(302, response.status_code)
