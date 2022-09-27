from django.http import HttpResponse


def add_route(request):
    return HttpResponse("<h1>Add route</h1>")


def detail_route(request, id_route):
    return HttpResponse("<h1>Detail route</h1>")


def add_event_route(request, id_route):
    return HttpResponse("<h1>Add event</h1>")


def filter_route(request, route_type=None, country=None, location=None):
    return HttpResponse("<h1>Filter route</h1>")


def review_route(request, id_route):
    return HttpResponse("<h1>Reviews route</h1>")


def event_handler(request):
    return HttpResponse("<h1>Event handler</h1>")
