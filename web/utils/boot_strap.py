# coding:utf-8
import logging
import time
import json
import requests
from django.conf import settings
from web.utils.config_util import get_docker_proxy_url
from web.utils.config_util import get_network_name
from web.utils.config_util import get_zk_hosts
from web.utils.zk_util import get_min_cluster
from web.models.res import Compute
from web.utils.rest_util import yarn_is_active
from web.utils.rest_util import AzbakanHTTPPost
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
    payload = {
        "image": image,
        "mem_limit": memory,
        "network_name": get_network_name(),
        "environment": environment
    }
    request_url = url + '/containers/'
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
    request_url = url + '/containers/'
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
    request_url = url + '/containers/'
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
    request_url = url + '/containers/'
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
    return requests.post(url + "/containers/", json=payload)


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
    request_url = url + '/containers/'
    return requests.post(request_url, json=payload)


def kill_container_by_id(container_id):
    try:
        url = get_docker_proxy_url()
        request_url = url + '/containers/{}'.format(container_id)
        requests.delete(request_url)
    except Exception as e:
        logger.warning(e)


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
        price = price_dict[job.job_priority]
        if price > cost:
            url = "http://" + min_cluster['ip'] + ":" + str(az_port)
            yarn_online = yarn_is_active(url)
            wait_time = 0
            while not yarn_online:
                logger.info("wait for RM online...")
                time.sleep(2)
                wait_time += 2
                yarn_online = yarn_is_active(url)
                if wait_time > 360:
                    break
            if yarn_online:
                az_result = az_submit(min_cluster['ip'], job)
                if az_result:
                    execute = Execute(user=job.user, job=job,
                                      computer_ip=min_cluster['ip'],
                                      storage_ip=storage.master_ip,
                                      execute_log='')
                    execute.save()
                    return 'Job has been submited successfully!'
                else:
                    logger.warning("Submit job to Azkaban Failed!")
                    return 'Submit job to Azkaban Failed!'
            else:
                logger.warning("Boot RM succeed, but not on service.")
                return 'Boot RM succeed, but not on service.'
        else:
            return launch_by_new(storage, user_id, az_port, job)


def launch_by_new(storage, user_id, az_port, job):
    result = boot_compute_yarn_master(storage.master_ip, user_id)
    result = json.loads(result.json())
    status = result['status']
    if status == 'success':
        container_id = result['Id']
        ip = result['IPAddress']
        garbage = Compute.objects.filter(master_ip=ip)
        for container in garbage:
            container.delete()
        compute = Compute(user=job.user, container_id=container_id,
                          master_ip=ip, storage=storage)
        compute.save()
        # check service
        url = "http://" + ip + ":" + str(az_port)
        yarn_online = yarn_is_active(url)
        wait_time = 0
        while not yarn_online:
            logger.info("wait for RM online...")
            print("waitting...")
            time.sleep(2)
            wait_time += 2
            yarn_online = yarn_is_active(url)
            if wait_time > 180:
                break
        if yarn_online:
            print("try to submit job to az")
            az_result = az_submit(ip, job)
            if az_result:
                execute = Execute(user=job.user, job=job, computer_ip=ip,
                                  storage_ip=storage.master_ip, execute_log='')
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


def az_submit(host_ip, job):
    try:
        az_port = getattr(settings, 'AZ_PORT', 8081)
        az_timeout = getattr(settings, 'AZ_TIMEOUT', 30)
        params = {'action': 'login', 'username': 'shida', 'password': 'shida'}
        http_client = AzbakanHTTPPost(host_ip, az_port, az_timeout)
        # login azbakan
        response = http_client.post('/', params)
        session = response.json()
        session_id = session['session.id']
        params = {'session.id': session_id,
                  'name': job.job_name,
                  'description': job.job_desc}
        http_client.post('/manager?action=create', params)
        http_client.upload('/manager', session_id, job.job_name, job.job_file)
        response = http_client.get('/manager?session.id=' + session_id +
                                   '&ajax=fetchprojectflows&project=' +
                                   job.job_name)

        flows = response.json()
        response = http_client.get('/executor?session.id=' + session_id +
                                   '&ajax=executeFlow&project=' +
                                   job.job_name + '&flow=' +
                                   flows['flows'][0]['flowId'])

        return True
    except Exception as e:
        print(e)
        logger.error(e)
        return False
