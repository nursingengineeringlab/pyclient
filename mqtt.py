import json
import queue
import atexit
import time
from logger import Logger
import senior
import math
import asyncio
import websockets
import argparse
import os
import multiprocessing
from random import randint
import paho.mqtt.client as mqtt
import ecg_pb2
from config import base_ip, base_ip, mqtt_port

# 连接成功回调
def on_connect(client, userdata, flags, rc):
    print('Connected with result code '+str(rc))
    client.subscribe('testtopic/#')

# 消息接收回调
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))



# seed random number generator
# generate some integers

senior_queue = queue.Queue()
UPDATE_DATA_TIMEOUT = 1

def current_milli_time():
    return round(time.time() * 1000)


# On program exit delete users from database
def exit_handler():
    print("Deleting Seniors")
    for s in senior_queue.queue:
        senior.senior_manager.delete_senior(s, api_url)
    print("End")


class TestECG(Logger):
    def __init__(self, num_senior, url):
        Logger.__init__(self, "Main")
        self.num_senior = num_senior
        self.update_percentage = math.ceil(num_senior * 0.15)
        self.debug("Test ECG")
        self.last_ping_time = 0
        self.last_data_update_time = int(time.time())
        self.api_url = url
        seniors = senior.senior_manager.get_senior(num_senior)

        if len(seniors) == 0:
            print("create new seniors")
            seniors = [senior.senior_manager.make_senior(self.api_url) for _ in range(num_senior)]

        for s in seniors:
            senior_queue.put(s)


    def run(self, mqttc):
        counter = 0
        flip_second = 5
        packet = ecg_pb2.ECGPacket()
        packet.command = ecg_pb2.ECGPacket.CommandType.NEW
        while True:
            for s in senior_queue.queue:
                if int(time.time()) - s.last_data_update_time > UPDATE_DATA_TIMEOUT:
                    new_rand_rri = randint(800, 1250)
                    new_rand_temp = randint(96, 99)
                    packet.device_id = s.id
                    packet.sequence_id = s.seq
                    packet.value = new_rand_rri if counter % flip_second else new_rand_temp
                    packet.battery = 60
                    packet.active = True
                    packet.data_type = packet.DataType.RRI if counter % flip_second else packet.DataType.TEMP
                    packet.time = int(round(time.time() * 1000))
                    mqttc.publish('emqtt',payload=packet.SerializeToString(),qos=0)
                    s.last_data_update_time = int(time.time())
                    s.seq = s.seq + 1
                    counter = counter + 1
                    packet.command = ecg_pb2.ECGPacket.CommandType.UPDATE


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='args.')
    parser.add_argument('-n', '--num', type=int, default=1)
    parser.add_argument('-d', '--dele', default=True)
    parser.add_argument('-u', '--url', type=str, default='nelab.ddns.umass.edu/')
    parser.add_argument('--port', type=int, default=8000)

    print("Number of cpu :", multiprocessing.cpu_count())
    args = parser.parse_args()
    api_url =  "https://" + base_ip + "/"

    input_num = args.num
    if args.dele is True:
        try:
            os.remove("./data_store/test.txt")
        except OSError:
            pass

        with open("./data_store/test.txt", 'a') as results_file:
            pass
    
    client = mqtt.Client()

    # 指定回调函数
    client.on_connect = on_connect
    client.on_message = on_message

    # 建立连接
    client.tls_set()
    client.connect(base_ip, int(mqtt_port), 60)
    # 发布消息


    atexit.register(exit_handler)
    test_run = TestECG(input_num, api_url)
    test_run.run(client)
    
    # client.loop_forever()

