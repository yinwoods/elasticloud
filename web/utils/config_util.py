# from web.utils import zk_util
from django.conf import settings


def get_zk_hosts():
    return getattr(settings, "ZK_HOSTS", "")


def get_network_name():
    return getattr(settings, "NETWORK_NAME", "")


def get_docker_proxy_url():
    # return zk_util.get_data("/EC_ROOT/DOCKER_PROXY")
    return "http://192.168.211.159:5000"
