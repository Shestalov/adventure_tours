import json
import datetime
from django.core.exceptions import ValidationError


def validation_date(value):
    try:
        parsed_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except BaseException:
        raise ValidationError('Incorrect type of date')

    if datetime.date.today() > parsed_date:
        raise ValidationError('Date must be greater than or equal to today')


def validation_stopping(value):
    try:
        stopping = json.loads(value)
        for itm in stopping:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValidationError("Incorrect json in 'Stopping points'")
    except BaseException:
        raise ValidationError('"Stopping points" is not in json')


def validation_route_type(value):
    if value not in ['hiking', 'cycling']:
        raise ValidationError("Incorrect route type try 'hiking' or 'cycling'")
