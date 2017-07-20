from rest_util import simple_post


def kill_container_by_id(id):
    try:
        url = "http://127.0.0.1:5000"
        params = {
            "id": id
        }
        simple_post(url + "/ws/containers/kill", params)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    result = kill_container_by_id('aaa042f20e2e')
    print(result)
