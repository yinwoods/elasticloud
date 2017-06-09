# coding:utf-8
import os, logging, time
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
            name = request.POST.get('name')
            description = request.POST.get('description')
            priority = request.POST.get('priority')
            upload_file = request.FILES.get('upload_file', None)
            if upload_file:
                dst = 'web/upload/' + user.__str__() + '/'
                if not os.path.exists(dst):
                    os.makedirs(dst)
                dst = dst + time.time().__str__() + '-' + upload_file.__str__()
                with open(dst, 'wb+') as destination:
                    for chunk in upload_file.chunks():
                        destination.write(chunk)
                job = Job(user=user, name=name, desc=description, file=dst, priority=priority)
                job.save()
                message = 'Submit success.'
        except Exception as e:
            message = 'Submit failed,cause by ' + e.message
            logger.error(e)
    return render(request, 'web/job/submit.html', {'message': message})


@login_required(login_url=LOGIN_URL)
def delete(request):
    if request.method == 'GET':
        try:
            id = request.GET.get('id')
            jobs = Job.objects.filter(id=id)
            for job in jobs:
                file = job.file
                os.remove(file)
                job.delete()
            return HttpResponse("true");
        except Exception as e:
            print e
            logger.warning(e.message)
            return HttpResponse("false");


@login_required(login_url=LOGIN_URL)
def launch(request):
    count = zk_util.count('/EC_ROOT/' + request.user.username + '/STORAGE/HDFS')
    if count == 0:
        print count
        return HttpResponse("No available HDFS resource.")
    hdfs_m_ip = zk_util.get_children('/EC_ROOT/' + request.user.username + '/STORAGE/HDFS')[0]
    storage = Storage.objects.filter(m_ip=hdfs_m_ip)
    print('-' * 50, 'in job launch', '-' * 50)
    print(request.__dict__)
    print('-' * 100)
    job = Job.objects.get(id=int(request.GET.get('id')))
    success = launch_job(job, storage[0], request.user.username)
    return HttpResponse(success);


@login_required(login_url=LOGIN_URL)
def list(request):
    lines = Job.objects.filter(user=request.user).order_by('-submit_time')
    return render(request, 'web/job/list.html', {'lines': lines})


@login_required(login_url=LOGIN_URL)
def execute(request):
    lines = Execute.objects.filter(user=request.user).order_by('-execute_time')
    return render(request, 'web/job/execute.html', {'lines': lines})


@login_required(login_url=LOGIN_URL)
def execute_delete(request):
    if request.method == 'GET':
        try:
            id = request.GET.get('id')
            executes = Execute.objects.filter(id=id)
            for exe in executes:
                exe.delete()
            return HttpResponse("true");
        except Exception as e:
            print e
            logger.warning(e.message)
            return HttpResponse("false");
