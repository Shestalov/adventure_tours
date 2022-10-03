from django.db import models
from django.utils.translation import gettext_lazy


class Place(models.Model):
    name = models.CharField(max_length=50)
    info = models.TextField(max_length=255)


class Route(models.Model):
    class RouteType(models.TextChoices):
        bicycle_route = 'bicycle', gettext_lazy('bicycle')
        hiking_route = 'hiking', gettext_lazy('hiking')

    route_type = models.CharField(max_length=50, choices=RouteType.choices, default=RouteType.hiking_route)
    departure = models.IntegerField()
    stopping = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.IntegerField()

    def __str__(self):
        return f'Route {self.id}'

    class Meta:
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'


class Event(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    event_admin = models.IntegerField()
    approved_users = models.JSONField()
    pending_users = models.JSONField()
    start_date = models.DateField()
    price = models.IntegerField()

    def __str__(self):
        return f'Event {self.id}'

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'


class Review(models.Model):

    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    route_review = models.TextField()
    route_rate = models.IntegerField()

    def __str__(self):
        return f'Review {self.id}'

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
