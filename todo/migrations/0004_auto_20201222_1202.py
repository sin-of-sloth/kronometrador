# Generated by Django 3.1.4 on 2020-12-22 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0003_quote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='speaker',
            field=models.TextField(blank=True),
        ),
    ]
