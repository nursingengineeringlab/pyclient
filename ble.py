from bluepy import btle
from binascii import hexlify
import time, uuid, json, requests
from logger import Logger
from enum import Enum
import threading
from config import request_headers, base_url, base_ip, mqtt_port
import paho.mqtt.client as mqtt
from threading import Timer
import ecg_pb2
import ssl

# Definitions   
BASE_UUID       =  uuid.UUID('6E400000-B5A3-F393-E0A9-E50E24DCCA9E') # never used
SERVICE_UUID    =  uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
WRITE_CHR_UUID  =  uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E') # never used
NOTIFY_CHR_UUID =  uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
TARGET_NAME     =  'MZB24C20R(A)'
HEART_BEAT_INTERVAL = 10 # seconds

class HeartBeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class DataType(str, Enum):
    RRI = 'RRI'
    TEMP = 'TEMP'
    SPO2 = 'SPO2'

dev_lock = threading.Lock()
# shared multipthread global 
device_list = []
log = Logger("BLE")
ws = None

client_id = "hcm_edge"


client = mqtt.Client(client_id)

seq_counter = 1


def on_connect(client, userdata, flags, rc):
    print('Connected with result code '+str(rc))
    client.subscribe('testtopic/#')


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


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

# def ws_send_data(command, device_id, value, data_type, active):
#     data = {
#         "command": command,
#         "device_id": device_id,
#         "time": int(time.time()),
#         "value" : value,
#         "data_type": data_type,
#         "active": active,
#         "battery" : 60,
#     }
#     json_string = json.dumps(data)
#     ws.send(json_string)

def mqtt_send_data(command, device_id, value, data_type, active):
    global seq_counter
    packet = ecg_pb2.ECGPacket()
    packet.command = ecg_pb2.ECGPacket.CommandType.UPDATE if command == "update" else ecg_pb2.ECGPacket.CommandType.CLOSE
    packet.device_id = device_id
    packet.sequence_id = seq_counter
    seq_counter = seq_counter + 1
    packet.value = value
    packet.battery = 60
    packet.active = active
    packet.data_type = packet.DataType.RRI if data_type == DataType.RRI else packet.DataType.TEMP
    packet.time = int(round(time.time() * 1000))
    client.publish('emqtt', payload=packet.SerializeToString(), qos=0)


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
            # print("val")
            mqtt_send_data("update", self.dev_name, val, DataType.RRI, True)
        elif data[16] == 0xAB:
            val = parse_measure_data(data)
            # print(f"Temperature: {val}")
            self.send_interval = self.send_interval + 1
            # send out temperatue only 5s interval
            if self.send_interval % 5 == 0:
                mqtt_send_data("update", self.dev_name, val, DataType.TEMP, True)
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


def device_handler(dev):
    try:
        with dev_lock:
            device_list.append(dev.addr)
            periph = btle.Peripheral(dev, "random")
            log.debug(f"Found Mezoo Device Mac Address: {dev.addr}")
            periph.setDelegate(DeviceDelegate(dev.addr, 0))

            # Setup to turn notifications on
            svc = periph.getServiceByUUID(SERVICE_UUID)
            ch = svc.getCharacteristics(NOTIFY_CHR_UUID)[0]
            periph.writeCharacteristic(ch.getHandle()+1, b"\x01\x00", True)
        while True:
            if periph.waitForNotifications(1.0):
                continue

    except (btle.BTLEException, btle.BTLEDisconnectError, Exception, UnboundLocalError) as e:
        log.debug(e)
        pass
    finally:
        mqtt_send_data("close", mac_address_to_name(dev.addr), 0, DataType.RRI, False)
        with dev_lock:
            if dev.addr in device_list:
                device_list.remove(dev.addr)
            periph.disconnect()
            log.debug(f"Mezoo Device Mac Address: {dev.addr} disconnected")
        return
    

if __name__ == "__main__":
    # websocket.enableTrace(True)

    client.on_connect = on_connect
    client.on_message = on_message
    # client.tls_set("./api-tls.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
    # client.tls_insecure_set(True)
    # client.tls_set()
    client.connect(base_ip, int(mqtt_port), 60)

    log.debug("Starting BLE Receiver")
    scanner = btle.Scanner().withDelegate(ScanDelegate())

    while True:
        try:
            devices = scanner.scan(5.0, passive=True)
            for dev in devices:
                if dev.addr not in device_list:
                    dev_data = dev.getScanData()
                    if len(dev_data) < 2 or len(dev_data[1]) < 3:
                        # log.debug("dev_data is too short, not Mezoo device")
                        # log.debug(dev_data)
                        continue

                    dev_name = dev_data[1][2] or None
                    if dev_name == TARGET_NAME:
                        handler = threading.Thread(target=device_handler, args=(dev,), daemon=True)
                        handler.start()
                    else:
                        pass
        except btle.BTLEDisconnectError as e:
            log.debug(e)
            pass