import urllib
import pycurl
import requests
# import StringIO
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
        # http_client = httplib.HTTPConnection(host, port)
        # http_client.request("POST", rest, params, headers)
        # response = http_client.getresponse()
        response = requests.post(rest, params, headers)
        return response.text
    except Exception as e:
        logger.error(e)
        return e.message
    finally:
        if http_client:
            http_client.close()


def simple_get(url):
    b = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.CUSTOMREQUEST, 'GET')
    c.setopt(c.WRITEFUNCTION, b.write)
    c.perform()
    return b.getvalue()


def az_post(host, port, timeout, path, params, headers=None):
    try:
        if headers:
            headers = headers
        else:
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"
            }
        session = requests.Session()
        session.headers = headers
        request_url = 'http://' + host + ':' + str(port) + path
        print('request_url: ', request_url)
        return session.post(request_url, headers=headers, data=params)
    except Exception as e:
        logger.error(e)
        return e


def az_upload(url, session, project, files):
    print(session)
    data = {
        'session.id': session,
        'ajax': 'upload'
    }
    files = {
        'file': open(files, 'rb')
    }
    response = requests.post(url, files=files, data=data)
    print(response.text)
    return response.text


def yarn_is_active(url):
    try:
        status_code = requests.get(url).status_code
        return status_code == 200
    except Exception as e:
        return False
