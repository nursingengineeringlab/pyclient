import requests
import queue
import threading
import json

api_user = "test1"
api_password = "test"
<<<<<<< HEAD
api_url =  "http://" + base_url + ":" + port + "/"
=======

>>>>>>> fix import url circle
request_headers = {'Content-Type': 'application/json'}
api_url = ''

class ApiHandler(threading.Thread):
	def __init__(self, url):
		super(ApiHandler, self).__init__()
		self.__output_queue = queue.Queue()
		self.__function_queue = queue.Queue()
		self.timeout = 1.0/60
		self.api_url = url

	def onThread(self, function, *args, **kwargs):
		self.__function_queue.put((function, args, kwargs))

	def create_senior(self, data):
		r = requests.post(self.api_url+"seniors/", headers=request_headers, auth=(api_user, api_password), data=data)
		if r.status_code == 201:
			return True
		else:
			print(r.json())
			return False

	def delete_user(self, device_id):
		r = requests.delete(self.api_url+"seniors/"+device_id, auth=(api_user, api_password))

	def send_data(self, senior):
		device_type = senior.device.type.name
		data = senior.get_data()
		url = self.api_url + "sensordata/" + device_type + '/'
		r = requests.post(url, headers=request_headers, auth=(api_user, api_password), data=json.dumps(data))

	def send_ping(self, senior):
		data = {
			"device_id": senior.id,
			"battery": senior.get_battery(),
		}
		url = self.api_url + "ping/"
		r = requests.post(url, headers=request_headers, auth=(api_user, api_password), data=json.dumps(data))

	def run(self):
		print("Starting API Handler")
		while True:
			try:
				# Get functions called on this thread
				function, args, kwargs = self.__function_queue.get(timeout=self.timeout)
				function(*args, **kwargs)			
			except Exception as e:
				pass


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


