# coding:utf-8
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from elasticloud.settings import LOGIN_URL
from django.http import HttpResponse
from web.utils import zk_util

# Common
logger = logging.getLogger(__name__)


@login_required(login_url=LOGIN_URL)
def index(request):
    summary = {}
    summary['compute_count'] = get_compute_count(request.user.username).__str__()
    summary['storage_count'] = get_storage_count(request.user.username).__str__()
    print summary
    return render(request, 'web/index.html', summary)


def get_compute_count(username):
    count = zk_util.count('/EC_ROOT/' + username + '/COMPUTE')
    return count if count else 0


def get_storage_count(username):
    count = zk_util.count('/EC_ROOT/' + username + '/STORAGE/HDFS')
    count += zk_util.count('/EC_ROOT/' + username + '/STORAGE/HBASE')
    return count if count else 0
