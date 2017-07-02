from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_name = models.CharField(max_length=30)
    job_desc = models.CharField(max_length=30)
    job_file = models.CharField(max_length=1000)
    job_priority = models.IntegerField(default=2)
    job_stat = models.CharField(max_length=30, default='Ready')
    job_submit_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'web'


class Execute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    computer_ip = models.CharField(max_length=50)
    storage_ip = models.CharField(max_length=50)
    execute_log = models.TextField()
    execute_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'web'
