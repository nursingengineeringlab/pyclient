import sys
import requests
from apihandler import custom_senior_delete
from config import base_url, request_headers


def cleanup_users():
    r = requests.get(base_url+"seniors/?format=json", headers=request_headers)
    print(r.json())
    for rs in r.json()['results']:
        print(rs['device_id'])
        custom_senior_delete(rs['device_id'], base_url)

def cleanup_user(device_id):
    custom_senior_delete(device_id, base_url)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Incomplete arguments")
        exit()

    input_str = sys.argv[1]

    if input_str == 'all':
        cleanup_users()
    else:
        custom_senior_delete(input_str, base_url)