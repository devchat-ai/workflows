import requests
import os
from functools import wraps

BASE_SERVER_URL = os.environ.get("DEVCHAT_IDE_SERVICE_URL", "http://localhost:3000")


def rpc_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        function_name = f.__name__
        url = f"{BASE_SERVER_URL}/{function_name}"

        data = dict(zip(f.__code__.co_varnames, args))
        data.update(kwargs)
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Server error: {response.status_code}")

        response_data = response.json()
        if "error" in response_data:
            raise Exception(f"Server returned an error: {response_data['error']}")
        return response_data["result"]

    return wrapper


@rpc_call
def get_lsp_brige_port():
    pass
