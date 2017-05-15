# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Credentials(models.Model):
    id = models.ForeignKey(User, primary_key=True,unique=True)
    credential = models.CharField(max_length=2000)


class Sales_person_freetimes(models.Model):
    id = models.ForeignKey(User)
    TimeZone = models.CharField(max_length=100)
    start_time = models.DateTimeField()

class Calendar_request(models.Model):
    customer_id = models.ForeignKey(User)
    allotted_sales_rep = models.ForeignKey(User)
    customer_sales_person_free_time = models.ForeignKey(Sales_person_freetimes)
