auth_token = '9208805fe4ba3e2d89f33777fc969d2727f26351'
request_headers = {'Content-Type': 'application/json', 'Authorization': 'Token '+ auth_token}
test_device_id      = "F43053011ACF"
test_device_type    = "RRI"
filename = "./data_store/test.txt"


base_ip = "nelab.ddns.umass.edu"
mqtt_port = "30482"
base_port = "31000"
base_url = "http://" + base_ip + ":" + base_port + "/"
ws_url = "ws://" + base_ip + ":" + base_port + "/ws/sensor/RR"

