import httplib, urllib, pycurl, StringIO, logging

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
        http_client = httplib.HTTPConnection(host, port)
        http_client.request("POST", rest, params, headers)
        response = http_client.getresponse()
        str_t = response.read()
        return str_t
    except Exception as e:
        logger.error(e)
        return e.message
    finally:
        if http_client:
            http_client.close()


def simple_get(url):
    print('x' * 100)
    print('in simple_get')
    print(url)
    print('x' * 100)
    b = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.CUSTOMREQUEST, 'GET')
    c.setopt(c.WRITEFUNCTION, b.write)
    c.perform()
    return b.getvalue()


def az_post(host, port, timeout, path, params, headers=None):
    http_client = None
    try:
        params = urllib.urlencode(params)
        if headers:
            headers = headers
        else:
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"
            }
        http_client = httplib.HTTPConnection(host, port, timeout=timeout)
        print('x' * 100)
        print('in az_post')
        print(host, port, timeout, path, params)
        print('x' * 100)
        http_client.request("POST", path, params, headers)
        response = http_client.getresponse()
        str_t = response.read()
        return str_t
    except Exception as e:
        logger.error(e)
        return e
    finally:
        if http_client:
            http_client.close()


def az_upload(url, session, project, file):
    b = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.CUSTOMREQUEST, 'POST')
    c.setopt(c.WRITEFUNCTION, b.write)
    c.setopt(c.HTTPHEADER, ['Content-Type:multipart/mixed'])
    c.setopt(
        c.HTTPPOST,
        [
            ('file', (c.FORM_FILE, file)),
            ('session.id', (c.FORM_CONTENTS, session)),
            ('project', (c.FORM_CONTENTS, project)),
            ('ajax', (c.FORM_CONTENTS, 'upload'))
        ]
    )
    c.perform()
    return b.getvalue()


def isOnService(url):
    try:
        statusCode = urllib.urlopen(url).getcode()
        return statusCode == 200
    except Exception as e:
        return False
