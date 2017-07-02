# coding:utf-8
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from elasticloud.settings import LOGIN_URL
from web.models.res import Compute
from web.utils import boot_strap
from django.http import HttpResponse

# Cluster management
logger = logging.getLogger(__name__)


@login_required(login_url=LOGIN_URL)
def list(request):
    lines = Compute.objects.filter(user=request.user).order_by('-date')
    return render(request, 'compute_list.html', {'lines': lines})


@login_required(login_url=LOGIN_URL)
def delete(request):
    if request.method == 'GET':
        try:
            container_id = request.GET.get('container_id')
            compute = Compute.objects.get(container_id=container_id)
            boot_strap.kill_container_by_id(container_id)
            compute.delete()
            return HttpResponse("true")
        except Exception as e:
            print(e)
            logger.warning(e.message)
            return HttpResponse("false")
