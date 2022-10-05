# Generated by Django 4.1.1 on 2022-10-03 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0003_alter_route_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'Event', 'verbose_name_plural': 'Events'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'verbose_name': 'Review', 'verbose_name_plural': 'Reviews'},
        ),
        migrations.AlterModelOptions(
            name='route',
            options={'verbose_name': 'Route', 'verbose_name_plural': 'Routes'},
        ),
        migrations.AlterField(
            model_name='event',
            name='route_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='route.route'),
        ),
    ]
