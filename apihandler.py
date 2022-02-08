import requests


request_headers = {'Content-Type': 'application/json', 'Authorization': 'Token dd94c6e20c9ee32164e25dffca225e78028047c1'}

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


