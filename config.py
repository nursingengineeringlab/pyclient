
auth_token = 'dd94c6e20c9ee32164e25dffca225e78028047c1'
request_headers = {'Content-Type': 'application/json', 'Authorization': 'Token '+ auth_token}
test_device_id      = "F43053011ACF"
test_device_type    = "RRI"
filename = "./data_store/test.txt"


#base_ip = "127.0.0.1"
base_ip = "172.24.41.203"
base_port = "8000"
base_url = "http://" + base_ip + ":" + base_port + "/"
ws_url = "ws://" + base_ip + ":" + base_port + "/ws/sensor/RR"
