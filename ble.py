from bluepy import btle
from binascii import hexlify
import time, uuid, json, requests
from logger import Logger
from enum import Enum
import threading
import websocket
from config import request_headers, ws_url, base_url

# Definitions   
BASE_UUID       =  uuid.UUID('6E400000-B5A3-F393-E0A9-E50E24DCCA9E') # never used
SERVICE_UUID    =  uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
WRITE_CHR_UUID  =  uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E') # never used
NOTIFY_CHR_UUID =  uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
TARGET_NAME     =  'MZB24C20R(A)'

class DataType(str, Enum):
    RRI = 'RRI'
    TEMP = 'TEMP'
    SPO2 = 'SPO2'


device_list = []
log = Logger("BLE")

ws = None

def mac_address_to_name(mac):
    return mac.replace(':', '').upper()


def api_send_data(device_id, value, device_type):
    data = {
        "device_id": device_id,
        "time": int(time.time()),
        "value" : value
    }
    url = base_url + "sensordata/" + device_type + '/'
    r = requests.post(url, headers=request_headers, data=json.dumps(data))

def ws_send_data(command, device_id, value, data_type, active):
    data = {
        "command": command,
        "device_id": device_id,
        "time": int(time.time()),
        "value" : value,
        "data_type": data_type,
        "active": active,
        "battery" : 60,
        "sequence_id": 1,
    }
    json_string = json.dumps(data)
    ws.send(json_string)

class ScanDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # pass
        if isNewDev:
            pass
            # print("Discovered device", dev.addr)
            # ws_send_data("new", test_device_id, 0, DeviceType.RRI)
        elif isNewData:
            pass
            # print("Received new data from", dev.addr)

class DeviceDelegate(btle.DefaultDelegate):
    def __init__(self, mac_address, interval):
        btle.DefaultDelegate.__init__(self)
        self.dev_name = mac_address_to_name(mac_address)
        self.send_interval = interval
        # ... initialise here

    def handleNotification(self, cHandle, data):
        parse_measure_data = lambda data : ((data[17] << 7))  | (data[18] & 0x7F)
        if data[16] == 0xA7:
            val = parse_measure_data(data)
            # print(f"RRI: {val}")
            #print(f'High: {data[17]}')
            #print(f'Low: {data[18]}')
            ws_send_data("update", self.dev_name, val, DataType.RRI, True)
        elif data[16] == 0xAB:
            val = parse_measure_data(data)
            # print(f"Temperature: {val}")
            self.send_interval = self.send_interval + 1
            # send out temperatue only 5s interval
            if self.send_interval % 5 is 0:
                ws_send_data("update", self.dev_name, val, DataType.TEMP, True)
        elif data[16] == 0x92:
            pass
            # val = parse_measure_data(data)
            # print(f"Heart Rate: {val}")
            # print("Heart Rate: No support API yet send to server")
        elif data[16] == 0x9D:
            pass
            # val = parse_measure_data(data)
            # print(f"Battery check: {val}")
            # print("Battery check: No support API yet send to server")
        else:
            pass
            # print("Received data %s " % hexlify(data))


def device_handler(devices):
    for dev in devices:
            dev_data = dev.getScanData()
            if len(dev_data) < 2 and len(dev_data[1]) < 3:
                print("dev_data is too short, not Mezoo device")
                # log.debug(dev_data)
                return

            dev_name = dev_data[1][2] or None
            # print("Another name :", )
            if dev_name == TARGET_NAME:
                try:
                    log.debug(f"Found Mezoo Device Mac Address: {dev.addr}")
                    periph = btle.Peripheral(dev, "random")     # supply scan entry as arg
                    periph.setDelegate(DeviceDelegate(dev.addr, 0))

                    # Setup to turn notifications on
                    svc = periph.getServiceByUUID(SERVICE_UUID)
                    ch = svc.getCharacteristics(NOTIFY_CHR_UUID)[0]
                    periph.writeCharacteristic(ch.getHandle()+1, b"\x01\x00", True)
                    
                    while True:
                        if periph.waitForNotifications(1.0):
                            continue
                finally:
                    ws_send_data("close", mac_address_to_name(dev.addr), 0, DataType.RRI, False)
                    periph.disconnect()
            else:
                pass

                # print("other bluetooth device ignore it")
        # except Exception as e:
        #     print(e)
        #     pass


if __name__ == "__main__":
    log.debug("Starting WebSocket")
    ws = websocket.WebSocket()


    print(ws_url)
    ws.connect(ws_url)

    log.debug("Starting BLE Receiver")
    scanner = btle.Scanner().withDelegate(ScanDelegate())
    # try:
    while True:
        devices = scanner.scan(5.0, passive=True)
        handler = threading.Thread(target=device_handler, args=(devices,), daemon=True)
        handler.start()
        time.sleep(2)
    # except Exception as e:
        # pass
