# coding:utf-8
import os
import logging
import time
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.http import HttpResponse
from elasticloud.settings import LOGIN_URL
from web.models.job import Job
from web.utils.boot_strap import launch_job
from web.models.job import Execute
from web.utils import zk_util
from web.models.res import Storage

# Job management
logger = logging.getLogger(__name__)


@login_required(login_url=LOGIN_URL)
def submit(request):
    message = None
    if request.method == 'POST':
        try:
            user = request.user
            job_name = request.POST.get('job_name')
            job_desc = request.POST.get('job_desc')
            job_priority = request.POST.get('job_priority')
            job_file = request.FILES.get('job_file', None)
            if job_file:
                dst = 'web/upload/' + user.__str__() + '/'
                if not os.path.exists(dst):
                    os.makedirs(dst)
                dst = dst + str(time.time()) + '-' + str(job_file)
                with open(dst, 'wb+') as destination:
                    for chunk in job_file.chunks():
                        destination.write(chunk)
                job = Job(user=user, job_name=job_name, job_desc=job_desc,
                          job_file=dst, job_priority=job_priority)
                job.save()
                message = 'Submit success.'
        except Exception as e:
            message = 'Submit failed,cause by ' + str(e)
            logger.error(e)
    return render(request, 'job_submit.html', {'message': message})


@login_required(login_url=LOGIN_URL)
def remove(request):
    if request.method == 'DELETE':
        try:
            request_params = QueryDict(request.body)
            job_id = request_params.get('job_id')
            jobs = Job.objects.filter(id=job_id)
            for job in jobs:
                job_file = job.job_file
                os.remove(job_file)
                job.delete()
            return HttpResponse("true")
        except Exception as e:
            logger.warning(e)
            return HttpResponse("false")


@login_required(login_url=LOGIN_URL)
def launch(request):
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        count = zk_util.count(
                '/EC_ROOT/' + request.user.username + '/STORAGE/HDFS')
        if count == 0:
            return HttpResponse("No available Storage resource.")
        hdfs_main_ip = zk_util.get_children(
                '/EC_ROOT/' + request.user.username + '/STORAGE/HDFS')[0]
        storage = Storage.objects.filter(main_ip=hdfs_main_ip)
        job = Job.objects.get(id=int(job_id))
        success = launch_job(job, storage[0], request.user.username)
        return HttpResponse(success)


@login_required(login_url=LOGIN_URL)
def list(request):
    lines = Job.objects.filter(user=request.user).order_by('-submit_time')
    return render(request, 'job_list.html', {'lines': lines})


@login_required(login_url=LOGIN_URL)
def execute(request):
    lines = Execute.objects.filter(user=request.user).order_by('-execute_time')
    return render(request, 'job_execute.html', {'lines': lines})


@login_required(login_url=LOGIN_URL)
def execute_remove(request):
    if request.method == 'DELETE':
        try:
            request_params = QueryDict(request.body)
            job_id = request_params.get('job_id')
            executes = Execute.objects.filter(id=job_id)
            for exe in executes:
                exe.delete()
            return HttpResponse("true")
        except Exception as e:
            print(e)
            logger.warning(e.message)
            return HttpResponse("false")
