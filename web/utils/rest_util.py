import urllib
import requests
import logging

logger = logging.getLogger(__name__)


def simple_post(url, params, headers=None):
    proto, rest = urllib.splittype(url)
    host, rest = urllib.splithost(rest)
    host, port = urllib.splitport(host)
    http_client = None
    try:
        params = urllib.urlencode(params)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        if headers:
            headers = headers
        response = requests.post(rest, params, headers)
        return response.text
    except Exception as e:
        logger.error(e)
        return e.message
    finally:
        if http_client:
            http_client.close()


class AzbakanHTTPPost():
    def __init__(self, host_ip, port, timeout):
        self.session = requests.Session()
        self.host_ip = host_ip
        self.port = port
        self.timeout = timeout

    def get(self, path, headers=None):
        if headers is None:
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"
            }
        self.session.headers = headers
        request_url = 'http://{host_ip}:{port}{path}'.format(
            host_ip=self.host_ip,
            port=self.port,
            path=path
        )
        print('request_url: ', request_url)
        return self.session.get(request_url, headers=headers)

    def post(self, path, params, headers=None):
        if headers is None:
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"
            }
        self.session.headers = headers
        request_url = 'http://{host_ip}:{port}{path}'.format(
            host_ip=self.host_ip,
            port=self.port,
            path=path
        )
        print('request_url: ', request_url)
        return self.session.post(request_url, headers=headers, data=params)

    def upload(self, path, session, project, files):
        print(session)
        headers = {
            'Content-Type': 'multipart/mixed'
        }
        data = {
            'session.id': session,
            'ajax': 'upload'
        }
        files = {
            'file': open(files, 'rb')
        }
        request_url = 'http://{host_ip}:{port}{path}'.format(
            host_ip=self.host_ip,
            port=self.port,
            path=path
        )
        response = self.session.post(request_url, headers=headers,
                                     files=files, data=data)
        print(response.text)
        return response.text


def yarn_is_active(url):
    try:
        status_code = requests.get(url).status_code
        return status_code == 200
    except Exception as e:
        return False
