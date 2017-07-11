"""elasticloud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from web.views import index
from web.views import account
from web.views import job
from web.views import storage
from web.views import compute

app_name = 'web'

urlpatterns = [

    # Index
    url(r'^$', index.index, name='index'),
    url(r'^index/$', index.index, name='index'),


    # Account
    url(r'^account/login/$', account.login, name='login'),
    url(r'^account/register/$', account.register, name='register'),
    url(r'^account/logout/$', account.logout, name='logout'),
    url(r'^account/forgot/$', account.forgot, name='forgot'),
    url(r'^account/check_duplicate/$', account.check_duplicate,
        name='check_duplicate'),
    url(r'^profile$', account.profile, name='profile'),


    # Job
    url(r'^job/list/$', job.list, name='job_list'),
    url(r'^job/execute/$', job.execute, name='job_execute^'),
    url(r'^job/execute/remove$', job.execute_remove,
        name='job_execute_remove'),

    url(r'^job/submit/$', job.submit, name='job_submit'),
    url(r'^job/launch/$', job.launch, name='job_launch'),
    url(r'^job/remove/$', job.remove, name='job_remove'),


    # Cluster
    url(r'^cluster/compute/list/$', compute.list, name='cluster_compute_list'),
    url(r'^cluster/compute/remove/$', compute.remove,
        name='cluster_compute_remove'),
    url(r'^cluster/storage/create/$', storage.create,
        name='cluster_storage_create'),
    url(r'^cluster/storage/list/$', storage.list, name='cluster_storage_list'),
    url(r'^cluster/storage/remove/$', storage.remove,
        name='cluster_storage_remove'),


]
