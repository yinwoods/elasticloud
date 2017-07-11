# coding:utf-8
import logging
import json
import time
import requests
from django.conf import settings
from web.utils.config_util import get_docker_proxy_url
from web.utils.config_util import get_network_name
from web.utils.config_util import get_zk_hosts
from web.utils.zk_util import get_min_cluster
from web.models.res import Compute
from web.utils.rest_util import isOnService, az_upload, az_post
from web.models.job import Execute

logger = logging.getLogger(__name__)


# USER_ID = username

def boot_storage_hdfs_master(USER_ID, memory):
    url = get_docker_proxy_url()
    image = "yinwoods/storage_hdfs_master:1.0"
    environment = {
        'ZK_HOSTS': get_zk_hosts(),
        'USER_ID': USER_ID
    }
    print('y' * 100)
    print(environment)
    print('y' * 100)
    payload = {
        "image": image,
        "mem_limit": memory,
        "network_name": get_network_name(),
        "environment": environment
    }
    request_url = url + '/ws/containers/create'
    return requests.post(request_url, json=payload)


def boot_storage_hdfs_slave(NAMENODE_IP, memory):
    url = get_docker_proxy_url()
    image = "yinwoods/storage_hdfs_slave:1.0"
    environment = {
        "NAMENODE_IP": NAMENODE_IP,
    }
    payload = {
        "image": image,
        "mem_limit": memory,
        "network_name": get_network_name(),
        "environment": environment
    }
    request_url = url + '/ws/containers/create'
    return requests.post(request_url, json=payload)


def boot_storage_hbase_master(USER_ID, memory):
    url = get_docker_proxy_url()
    image = "yinwoods/storage_hbase_master:1.0"
    environment = {
        'ZK_HOSTS': get_zk_hosts(),
        'USER_ID': USER_ID
    }
    payload = {
        "image": image,
        "mem_limit": memory,
        "network_name": get_network_name(),
        "environment": environment
    }
    request_url = url + '/ws/containers/create'
    return requests.post(request_url, json=payload)


def boot_storage_hbase_slave(USER_ID, memory):
    url = get_docker_proxy_url()
    image = "yinwoods/storage_hbase_slave:1.0"
    environment = {
        'ZK_HOSTS': get_zk_hosts(),
        'USER_ID': USER_ID
    }
    payload = {
        "image": image,
        "mem_limit": memory,
        "network_name": get_network_name(),
        "environment": environment
    }
    request_url = url + '/ws/containers/create'
    return requests.post(request_url, json=payload)


def boot_storage_nosql_master(USER_ID, memory):
    url = get_docker_proxy_url()
    image = "yinwoods/storage_nosql_master:1.0"
    environment = {
        'ZK_HOSTS': get_zk_hosts(),
        'USER_ID': USER_ID
    }
    payload = {
        "image": image,
        "mem_limit": memory,
        "network_name": get_network_name(),
        "environment": environment
    }
    return requests.post(url + "/ws/containers/create", json=payload)


def boot_compute_yarn_master(NAMENODE_IP, USER_ID):
    url = get_docker_proxy_url()
    image = "yinwoods/compute_yarn_master:1.0"
    environment = {
        "NAMENODE_IP": NAMENODE_IP,
        "DOCKER_PROXY_ADDRESS": url,
        "MEMORY": 1024,
        "VIRTUAL_CORE": 1,
        "USER_ID": USER_ID,
        "ZK_HOSTS": get_zk_hosts(),
        "YARN_SLAVE_IMAGE": "yinwoods/compute_yarn_slave:1.0",
        "DOCKER_NETWORK": get_network_name()
    }
    payload = {
        "image": image,
        "mem_limit": "1024MB",
        "network_name": get_network_name(),
        "environment": environment
    }
    request_url = url + '/ws/containers/create'
    return requests.post(request_url, json=payload)


def kill_container_by_id(container_id):
    try:
        url = get_docker_proxy_url()
        payload = {
            "id": container_id
        }
        request_url = url + '/ws/containers/kill'
        requests.post(request_url, json=payload)
    except Exception as e:
        logger.warning(e.message)


def launch_job(job, storage, user_id):
    # check available cluster
    az_port = getattr(settings, 'AZ_PORT', 8081)
    min_cluster = get_min_cluster(user_id)

    if min_cluster is None:
        return launch_by_new(storage, user_id, az_port, job)
    else:
        # calcute benefit
        cost = get_cost_by_scale(min_cluster['nodes'])
        price_dict = {1: 100, 2: 500, 3: 1000}
        price = price_dict[job.priority]
        if price > cost:
            url = "http://" + min_cluster['ip'] + ":" + az_port.__str__()
            on_line = isOnService(url)
            wait_time = 0
            while not on_line:
                logger.info("wait for RM online...")
                print("waitting...")
                time.sleep(2)
                wait_time += 2
                on_line = isOnService(url)
                if wait_time > 180:
                    break
            if on_line:
                print("try to submit job to az")
                az_result = az_submit(min_cluster['ip'], job)
                if az_result:
                    execute = Execute(user=job.user, job=job,
                                      c_ip=min_cluster['ip'],
                                      s_ip=storage.master_ip, execute_log='')
                    execute.save()
                    return 'Job has been submited successfully!'
                else:
                    logger.warning("Submit job to Azkaban Failed!")
                    return 'Submit job to Azkaban Failed!'
            else:
                print("not online")
                logger.warning("Boot RM succeed, but not on service.")
                return 'Boot RM succeed, but not on service.'
        else:
            return launch_by_new(storage, user_id, az_port, job)


def launch_by_new(storage, user_id, az_port, job):
    result = boot_compute_yarn_master(storage.master_ip, user_id)
    result = result.json()
    success = result['success']
    if success:
        container_id = result['data']['Id']
        ip = result['data']['IPAddress']
        garbage = Compute.objects.filter(master_ip=ip)
        for c in garbage:
            c.delete()
        compute = Compute(user=job.user, container_id=container_id,
                          master_ip=ip, storage=storage)
        compute.save()
        # check service
        url = "http://" + ip + ":" + az_port.__str__()
        on_line = isOnService(url)
        wait_time = 0
        while not on_line:
            logger.info("wait for RM online...")
            print("waitting...")
            time.sleep(2)
            wait_time += 2
            on_line = isOnService(url)
            if wait_time > 180:
                break
        if on_line:
            print("try to submit job to az")
            az_result = az_submit(ip, job)
            if az_result:
                execute = Execute(user=job.user, job=job, c_ip=ip,
                                  s_ip=storage.master_ip, execute_log='')
                execute.save()
                return 'Job has been submited successfully!'
            else:
                print("Submit job to Azkaban Failed!")
                kill_container_by_id(container_id)
                return 'Submit job to Azkaban Failed!'
        else:
            print("not online")
            kill_container_by_id(container_id)
            logger.warning("Boot RM succeed, but not on service.")
            return 'Boot RM succeed, but not on service.'
    else:
        logger.warning("Boot ResourceManager failed!")
        return "Boot ResourceManager failed!"


def get_cost_by_scale(node_number):
    return pow(node_number, 2)


def az_submit(address, job):
    try:
        az_port = getattr(settings, 'AZ_PORT', 8081)
        az_timeout = getattr(settings, 'AZ_TIMEOUT', 30)
        params = {'action': 'login', 'username': 'shida', 'password': 'shida'}
        session = json.loads(
                az_post(address, az_port, az_timeout, '/', params))
        print('x' * 100)
        print('in az_submit')
        print(session)
        print('x' * 100)
        session_id = session['session.id']
        params = {'session.id': session_id,
                  'name': job.name,
                  'description': job.desc}
        az_post(address, az_port, az_timeout, '/manager?action=create', params)
        az_upload('http://' + address + ':' + az_port.__str__() + '/manager',
                  session_id, job.name, job.file)
        flows = json.loads(
            requests.get('http://' + address + ':' + az_port.__str__() +
                         '/manager?session.id=' + session_id +
                         '&ajax=fetchprojectflows&project=' + job.name)
        )
        response = json.loads(requests.get(
            'http://' + address + ':' + az_port.__str__() +
            '/executor?session.id=' + session_id +
            '&ajax=executeFlow&project=' + job.name +
            '&flow=' + flows['flows'][0]['flowId'],
        ))
        print(response)

        return True
    except Exception as e:
        print(e)
        logger.error(e)
        return False
