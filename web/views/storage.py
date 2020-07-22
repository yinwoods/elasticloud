# coding:utf-8
import json
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import QueryDict
from elasticloud.settings import LOGIN_URL
from web.utils import boot_strap
from web.utils import zk_util
from web.models.res import Record
from web.models.res import Storage

# Cluster management
logger = logging.getLogger(__name__)


def create_storage(kwargs):

    storage_type = kwargs.get('storage_type')
    user = kwargs.get('user')
    main_memory = kwargs.get('main_memory')
    cluster_size = kwargs.get('cluster_size')
    subordinate_memory = kwargs.get('subordinate_memory')

    record = []
    message = None

    if storage_type == 'HDFS':
        response = boot_strap.boot_storage_hdfs_main(
                user.username, main_memory)
    elif storage_type == 'HBASE':
        response = boot_strap.boot_storage_hbase_main(
                user.username, main_memory)
    result = json.loads(response.json())
    status = result['status']
    if status == 'success':
        record.append(result['Id'])
        namenode_ip = result['IPAddress']
        for i in range(1, cluster_size):
            if storage_type == 'HDFS':
                response = boot_strap.boot_storage_hdfs_subordinate(
                        namenode_ip, subordinate_memory)
            elif storage_type == 'HBASE':
                response = boot_strap.boot_storage_hbase_subordinate(
                        namenode_ip, subordinate_memory)
            result = json.loads(response.json())
            status = result['status']
            if status == 'success':
                record.append(result['Id'])

        for container_id in record:
            rec = Record(container_id=container_id,
                         main_ip=namenode_ip)
            rec.save()
        garbage = Storage.objects.filter(main_ip=namenode_ip)
        for g in garbage:
            g.delete()
        storage = Storage(user=user, main_ip=namenode_ip,
                          main_memory=main_memory,
                          subordinate_memory=subordinate_memory,
                          cluster_size=cluster_size,
                          storage_type=storage_type)
        storage.save()
        message = 'Create Success'
    else:
        # roll back
        for id in record:
            boot_strap.kill_container_by_id(id)
        message = 'Create Failed'

    return message


@login_required(login_url=LOGIN_URL)
def create(request):
    message = None
    if request.method == 'POST':
        user = request.user
        storage_type = request.POST.get('type')
        cluster_size = int(request.POST.get('size'))
        main_memory = request.POST.get('m_memory')
        subordinate_memory = request.POST.get('s_memory')
        params = {
            'user': user,
            'cluster_size': cluster_size,
            'main_memory': main_memory,
            'subordinate_memory': subordinate_memory,
            'storage_type': storage_type,
        }
        print(params)
        message = create_storage(params)
    return render(request, 'storage_create.html',
                  {'message': message})


@login_required(login_url=LOGIN_URL)
def list(request):
    lines = []

    storage_ips = zk_util.get_children(
            '/EC_ROOT/' + request.user.username + '/STORAGE/HDFS')

    storage_ips += zk_util.get_children(
            '/EC_ROOT/' + request.user.username + '/STORAGE/HBASE')

    for main_ip in storage_ips:
        storage = Storage.objects.filter(main_ip=main_ip)
        if storage:
            lines.append(storage[0])
    return render(request, 'storage_list.html', {'lines': lines})


@login_required(login_url=LOGIN_URL)
def remove(request):
    if request.method == 'DELETE':
        try:
            delete = QueryDict(request.body)
            main_ip = delete.get('main_ip')
            recs = Record.objects.filter(main_ip=main_ip)
            for rec in recs:
                print(rec.container_id)
                boot_strap.kill_container_by_id(rec.container_id)
                rec.delete()
            storage = Storage.objects.filter(main_ip=main_ip)
            for sto in storage:
                sto.delete()
            return HttpResponse("true")
        except Exception as e:
            print(e)
            logger.warning(e)
            return HttpResponse("false")
