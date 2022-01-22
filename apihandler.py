import requests
import queue
import threading
import json

api_user = "test1"
api_password = "test"
api_url =  "http://" + base_url + ":" + port + "/"

request_headers = {'Content-Type': 'application/json'}
api_url = ''

# to be called from another thread on program exit
def custom_senior_delete(device_id, url):
	r = requests.delete(url+"seniors/"+device_id, auth=(api_user, api_password))


def custom_create_senior(data, url):
	r = requests.post(url+"seniors/", headers=request_headers, auth=(api_user, api_password), data=data)
	if r.status_code == 201:
		# print(r.json())
		return True
	else:
		# print(r.json())
		return False


