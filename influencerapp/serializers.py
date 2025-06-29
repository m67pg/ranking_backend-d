#!/usr/bin/env python3.7
from rest_framework import serializers
from .models import Influencer

class InfluencerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Influencer
        fields = '__all__'
