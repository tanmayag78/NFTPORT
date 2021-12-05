import requests


def make_requests(url, method, data=None, headers=None, params=None):
    """
    Make a request to the API.
    """
    headers = headers or {}
    if method == "GET":
        r = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        r = requests.post(url, headers=headers, data=data)
    else:
        raise Exception("Unsupported method: " + method)
    return r
