# coding:utf-8
import logging, json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from elasticloud.settings import LOGIN_URL
from web.utils import boot_strap
from web.utils import zk_util
from web.models.res import Record
from web.models.res import Storage

# Cluster management
logger = logging.getLogger(__name__)


@login_required(login_url=LOGIN_URL)
def create(request):
    message = None
    if request.method == 'POST':
        user = request.user
        type = request.POST.get('type')
        size = int(request.POST.get('size'))
        m_memory = request.POST.get('m_memory')
        s_memory = request.POST.get('s_memory')
        print(user.username)

        if type == '1':  # hdfs
            record = []
            result = boot_strap.boot_storage_hdfs_master(user.username, m_memory)
            result = json.loads(result)
            success = result['success']
            if success:
                record.append(result['data']['Id'])
                namenode_ip = result['data']['IPAddress']
                for i in range(1, size):
                    result = boot_strap.boot_storage_hdfs_slave(namenode_ip, s_memory)
                    result = json.loads(result)
                    success = result['success']
                    if success:
                        record.append(result['data']['Id'])

                for id in record:
                    rec = Record(c_id=id, m_ip=namenode_ip)
                    rec.save()
                garbage = Storage.objects.filter(m_ip=namenode_ip)
                for g in garbage:
                    g.delete()
                storage = Storage(user=user, m_ip=namenode_ip, m_mem=m_memory, s_mem=s_memory, size=size, type='HDFS')
                storage.save()
                message = 'Create Success'
            else:
                # roll back
                for id in record:
                    boot_strap.kill_container_by_id(id)
                message = 'Create Failed'

        elif type == '2':  # HBase
            record = []
            result = boot_strap.boot_storage_hbase_master(user.username, m_memory)
            result = json.loads(result)
            print('-' * 100)
            print('IN HBASE')
            print(result)
            print('-' * 100)
            success = result['success']
            if success:
                record.append(result['data']['Id'])
                namenode_ip = result['data']['IPAddress']
                for i in range(1, size):
                    result = boot_strap.boot_storage_hbase_slave(namenode_ip, s_memory)
                    result = json.loads(result)
                    success = result['success']
                    if success:
                        record.append(result['data']['Id'])

                for id in record:
                    rec = Record(c_id=id, m_ip=namenode_ip)
                    rec.save()
                garbage = Storage.objects.filter(m_ip=namenode_ip)
                for g in garbage:
                    g.delete()
                storage = Storage(user=user, m_ip=namenode_ip, m_mem=m_memory, s_mem=s_memory, size=size, type='HBASE')
                print('SAVE')
                print(storage.__dict__)
                storage.save()
                message = 'Create Success'
            else:
                # roll back
                for id in record:
                    boot_strap.kill_container_by_id(id)
                message = 'Create Failed'


        elif type == '3':  # NoSQL
            record = []
            result = boot_strap.boot_storage_hdfs_master(user.username, m_memory)
            result = json.loads(result)
            success = result['success']
            if success:
                record.append(result['data']['Id'])
                namenode_ip = result['data']['IPAddress']
                for i in range(1, size):
                    result = boot_strap.boot_storage_hdfs_slave(namenode_ip, s_memory)
                    result = json.loads(result)
                    success = result['success']
                    if success:
                        record.append(result['data']['Id'])

                for id in record:
                    rec = Record(c_id=id, m_ip=namenode_ip)
                    rec.save()
                garbage = Storage.objects.filter(m_ip=namenode_ip)
                for g in garbage:
                    g.delete()
                storage = Storage(user=user, m_ip=namenode_ip, m_mem=m_memory, s_mem=s_memory, size=size, type='HDFS')
                storage.save()
                message = 'Create Success'
            else:
                # roll back
                for id in record:
                    boot_strap.kill_container_by_id(id)
                message = 'Create Failed'
    return render(request, 'web/cluster/storage/create.html', {'message': message})


@login_required(login_url=LOGIN_URL)
def list(request):
    lines = []

    storage_ips = zk_util.get_children(
            '/EC_ROOT/' + request.user.username + '/STORAGE/HDFS')

    storage_ips += zk_util.get_children(
            '/EC_ROOT/' + request.user.username + '/STORAGE/HBASE')

    for m_ip in storage_ips:
        storage = Storage.objects.filter(m_ip=m_ip)
        if storage:
            lines.append(storage[0])
    return render(request, 'web/cluster/storage/list.html', {'lines': lines})


@login_required(login_url=LOGIN_URL)
def delete(request):
    if request.method == 'GET':
        try:
            m_ip = request.GET.get('m_ip')
            recs = Record.objects.filter(m_ip=m_ip)
            for rec in recs:
                boot_strap.kill_container_by_id(rec.c_id)
                rec.delete()
            storage = Storage.objects.filter(m_ip=m_ip)
            for sto in storage:
                sto.delete()
            return HttpResponse("true");
        except Exception as e:
            print e
            logger.warning(e.message)
            return HttpResponse("false");
