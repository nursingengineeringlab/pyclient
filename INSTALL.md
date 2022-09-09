# How to run bluetooth script on edge device (raspberry pi)


### Install venv (Ubuntu Linux)

```
python -m venv ./venv
```

### Install dependencies

```
pip3 install -r ./requirement.txt
```

### Make sure the config files are correct

```
vim config.py
```

```
auth_token = '5f9.........ea257fd02'
request_headers = {'Content-Type': 'application/json', 'Authorization': 'Token '+ auth_token}
test_device_id      = "F43053011ACF"
test_device_type    = "RRI"
filename = "./data_store/test.txt"
base_ip = "nelab.ddns.umass.edu"
mqtt_port = "30482"
base_url = "https://" + base_ip + "/"
```

make sure the auth_token is correct (find the auth_token in local storage in chrome browser)

### run ble.py

```
python3 ble.py
```

