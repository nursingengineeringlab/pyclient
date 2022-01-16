import sys
import requests
from apihandler import custom_senior_delete


base_url = "http://127.0.0.1:30007/"
request_headers = {'Content-Type': 'application/json'}
api_user = "test"
api_password = "test"


def cleanup_users():
    r = requests.get(base_url+"seniors/?format=json", headers=request_headers, auth=(api_user, api_password))
    print(r.json())
    for rs in r.json()['results']:
        print(rs['device_id'])
        custom_senior_delete(rs['device_id'])

def cleanup_user(device_id):
    custom_senior_delete(device_id)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Incomplete arguments")
        exit()

    input_str = sys.argv[1]

    if input_str == 'all':
        cleanup_users()
    else:
        custom_senior_delete(input_str)
    
