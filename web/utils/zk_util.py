# coding:utf-8
import logging
import json
import requests
import xml.etree.ElementTree as ET
from kazoo.client import KazooClient
from web.utils.config_util import get_zk_hosts

logging.basicConfig()
zk = KazooClient(hosts=get_zk_hosts())
zk.start()
print(zk.get_children('/'))


def init_schema(user_id):
    try:
        zk.ensure_path("/EC_ROOT")
        zk.create("/EC_ROOT/" + user_id)
        zk.create("/EC_ROOT/" + user_id + "/COMPUTE")
        zk.create("/EC_ROOT/" + user_id + "/STORAGE")
        zk.create("/EC_ROOT/" + user_id + "/STORAGE/HDFS")
    except Exception as e:
        logging.debug(e)


def get_data(path):
    if zk.exists(path):
        return zk.get(path)[0]
    return None


def count(path):
    if zk.exists(path):
        return len(zk.get_children(path))
    return 0


def get_children(path):
    if zk.exists(path):
        return zk.get_children(path)
    return []


def get_min_cluster(user_id):
    path = '/EC_ROOT/' + user_id + '/COMPUTE'
    min_nodes = float("inf")
    min_ip = ''
    children = get_children(path)
    if len(children) == 0:
        return None
    for child in children:
        try:
            url = "http://" + child + ":8088/ws/v1/cluster/metrics"
            response = requests.get(url)
            tree = ET.ElementTree(response.text)
            result = json.loads(tree.__dict__['_root'])
            active_nodes = int(result.get('clusterMetrics').get('activeNodes'))
            if active_nodes < min_nodes:
                min_nodes = active_nodes
                min_ip = child
        except Exception as e:
            print(e)
    if min_ip != '':
        return {'ip': min_ip, 'nodes': min_nodes}
    else:
        return None


if __name__ == "__main__":
    print(count("/EC_ROOT/test/COMPUTE"))
