from django.db import models
from django.utils.translation import gettext_lazy


class Place(models.Model):
    name = models.CharField(max_length=50)
    info = models.TextField(max_length=255)


class Route(models.Model):
    class RouteType(models.TextChoices):
        bicycle = 'bicycle', gettext_lazy('bicycle')
        hiking = 'hiking', gettext_lazy('hiking')

    route_type = models.CharField(max_length=50, choices=RouteType.choices, default=RouteType.hiking)
    departure = models.IntegerField()
    stopping = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.IntegerField()


class Event(models.Model):
    route_id = models.IntegerField()
    event_admin = models.IntegerField()
    approved_users = models.JSONField()
    pending_users = models.JSONField()
    start_date = models.DateField()
    price = models.IntegerField()
