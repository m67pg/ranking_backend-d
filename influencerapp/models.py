#!/usr/bin/env python3.7
from django.db import models

class Influencer(models.Model):
    username = models.CharField(max_length=255)
    followers = models.IntegerField()
    storeName = models.CharField(max_length=255, blank=True, null=True, db_column='store_name')
    popularity = models.IntegerField(default=0)
    region = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'influencers'
