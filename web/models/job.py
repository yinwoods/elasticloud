from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=30)
    file = models.CharField(max_length=1000)
    priority = models.IntegerField(default=2)
    stat = models.CharField(max_length=30, default='Ready')
    submit_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'web'


class Execute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    c_ip = models.CharField(max_length=50) # resourcemanager ip, compute
    s_ip = models.CharField(max_length=50) # namenode ip, storage
    execute_log = models.TextField()
    execute_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'web'
