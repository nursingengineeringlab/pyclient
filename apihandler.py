import requests


request_headers = {'Content-Type': 'application/json', 'Authorization': 'Token 79bfff7c4e78a575af2226fde003609680112e85'}

# to be called from another thread on program exit
def custom_senior_delete(device_id, url):
	r = requests.delete(url+"seniors/"+device_id, headers=request_headers)


def custom_create_senior(data, url):
	r = requests.post(url+"seniors/", headers=request_headers, data=data)
	if r.status_code == 201:
		# print(r.json())
		return True
	else:
		# print(r.json())
		return False


