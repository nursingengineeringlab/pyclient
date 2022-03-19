
auth_token = '9ae957eef83acf25817b315444be946a6d6826c4'
request_headers = {'Content-Type': 'application/json', 'Authorization': 'Token '+ auth_token}
test_device_id      = "F43053011ACF"
test_device_type    = "RRI"
filename = "./data_store/test.txt"


# base_ip = "nelab.ddns.umass.edu"
base_ip = "20.231.78.167"
base_port = "8000"
base_url = "http://" + base_ip + ":" + base_port + "/"
ws_url = "ws://" + base_ip + ":" + base_port + "/ws/sensor/RR"

