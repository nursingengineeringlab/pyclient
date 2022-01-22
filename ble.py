import os
from bluepy import btle 
from binascii import hexlify
import time, uuid, json, requests
from logger import Logger
from enum import Enum
import threading
import websocket

# Definitions   
BASE_UUID       =  uuid.UUID('6E400000-B5A3-F393-E0A9-E50E24DCCA9E') # never used
SERVICE_UUID    =  uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
WRITE_CHR_UUID  =  uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E') # never used
NOTIFY_CHR_UUID =  uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
TARGET_NAME     =  'MZB24C20R(A)'

class DeviceType(str, Enum):
    RRI = 'RRI'
    TEMP = 'TEMP'
    SPO2 = 'SPO2'


device_list = []
log = Logger("BLE")
request_headers = {'Content-Type': 'application/json', 'Authorization': 'Token 79bfff7c4e78a575af2226fde003609680112e85'}
base_url = "http://127.0.0.1:8000/"
test_device_id      = "2A648758F3D3"
test_device_type    = "RR"
ws = None

        
def api_send_data(device_id, value, device_type):
    data = {
        "device_id": device_id,
        "time": int(time.time()),
        "value" : value
    }
    url = base_url + "sensordata/" + device_type + '/'
    r = requests.post(url, headers=request_headers, data=json.dumps(data))

def ws_send_data(device_id, value, device_type):
    data = {
        "device_id": device_id,
        "time": int(time.time()),
        "value" : value,
        "battery" : 60,
        "sequence_id": 1,
    }
    
    ws.send(data)

class ScanDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        pass
        # if isNewDev:
        #     print("Discovered device", dev.addr)
        # elif isNewData:
        #     print("Received new data from", dev.addr)

class DeviceDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        #print(len(data))
        parse_measure_data = lambda data : ((data[17] << 7))  | (data[18] & 0x7F)
        if data[16] == 0xA7:
            val = parse_measure_data(data)
            print(f"RRI: {val}")
            #print(f'High: {data[17]}')
            #print(f'Low: {data[18]}')
            ws_send_data(test_device_id, val, DeviceType.RRI)
        elif data[16] == 0xAB:
            val = parse_measure_data(data)
            print(f"Temperature: {val}")
            ws_send_data(test_device_id, val, DeviceType.TEMP)
        elif data[16] == 0x92:
            val = parse_measure_data(data)
            print(f"Heart Rate: {val}")
            print("No support API yet send to server")
        elif data[16] == 0x9D:
            val = parse_measure_data(data)
            print(f"Battery check: {val}")
            print("No support API yet send to server")
        else:
            print("Received data %s " % hexlify(data))


def device_handler(devices, websocket):
    for dev in devices:
        try:
            dev_data = dev.getScanData()
            if len(dev_data) < 2 and len(dev_data[1]) < 3:
                print("dev_data is too short, not Mezoo device")
                log.debug(dev_data)
                return

            dev_name = dev_data[1][2] or None
            if dev_name == TARGET_NAME:
                log.debug("Found Mezoo Device")
                log.debug(f"Connecting to: {dev.addr}")
            
                periph = btle.Peripheral(dev, "random")     # supply scan entry as arg
                periph.setDelegate(DeviceDelegate())

                # Setup to turn notifications on
                svc = periph.getServiceByUUID(SERVICE_UUID)
                ch = svc.getCharacteristics(NOTIFY_CHR_UUID)[0]
                print("ch", ch)
                periph.writeCharacteristic(ch.getHandle()+1, b"\x01\x00", True)
                
                # while True:
                #     send_ping()
                #     if periph.waitForNotifications(1.0):
                #         continue
            else:
                pass
                # print("other bluetooth device ignore it")

        except Exception as e:
            print(e)
            pass


if __name__ == "__main__":
    log.debug("Starting WebSocket")
    ws = websocket.WebSocket()

    ws_url = "ws://" + base_url + "/ws/sensor/RR"

    ws.connect(ws_url)

    log.debug("Starting BLE Receiver")
    scanner = btle.Scanner().withDelegate(ScanDelegate())
    # try:
    while True:
        devices = scanner.scan(5.0, passive=True)
        handler = threading.Thread(target=device_handler, args=(devices, ws), daemon=True)
        handler.start()
        time.sleep(2)
    # except Exception as e:
        # pass