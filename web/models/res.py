import django.utils.timezone as timezone
from django.db import models
from django.contrib.auth.models import User


class Quota(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    memory = models.IntegerField(default=2048)

    class Meta:
        app_label = 'web'


class Record(models.Model):
    c_id = models.CharField(max_length=100)
    m_ip = models.CharField(max_length=20)

    class Meta:
        app_label = 'web'


class Storage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    m_ip = models.CharField(max_length=20)
    m_mem = models.CharField(max_length=20)
    s_mem = models.CharField(max_length=20)
    size = models.IntegerField(default=0)
    type = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'web'


class Compute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    c_id = models.CharField(max_length=100)
    m_ip = models.CharField(max_length=20)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'web'
