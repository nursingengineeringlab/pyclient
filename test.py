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

# seed random number generator
# generate some integers

base_url = ''
port = ''
api_url = ''
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
            seniors = [senior.senior_manager.make_senior(api_url) for _ in range(num_senior)]

        for s in seniors:
            senior_queue.put(s)


    async def run(self):
        url = websocket_url + 'ws/sensor/RR'
        async with websockets.connect(url) as websocket:
            test_json = {
                "command" : "new",
            }
            while True:
                for s in senior_queue.queue:
                    if int(time.time()) - s.last_data_update_time > UPDATE_DATA_TIMEOUT:
                        new_rand_value = randint(60, 120)
                        test_json["device_id"] = s.id
                        test_json["sequence_id"] = s.seq
                        test_json["value"] = new_rand_value
                        test_json["battery"] = 60
                        test_json["time"] = int(round(time.time() * 1000))
                        print(time.time())
                        print(len(json.dumps(test_json)))
                        print(time.time())
                        await websocket.send(json.dumps(test_json))
                        s.last_data_update_time = int(time.time())
                        s.seq = s.seq + 1
                        test_json["command"] = "update"


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='args.')
    parser.add_argument('-n', '--num', type=int, default=1)
    parser.add_argument('-d', '--dele', default=True)
    parser.add_argument('-u', '--url', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)

    print("Number of cpu :", multiprocessing.cpu_count())
    args = parser.parse_args()
    base_url = args.url
    port = str(args.port)
    websocket_url = "ws://" + base_url + ":" + port + "/"
    api_url =  "http://" + base_url + ":" + port + "/"
    print(api_url)
    # logger = logging.getLogger('websockets')
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(logging.StreamHandler())
    # print(websocket_url)

    input_num = args.num
    if args.dele is True:
        try:
            os.remove("./data_store/test.txt")
        except OSError:
            pass

        with open("./data_store/test.txt", 'a') as results_file:
            pass

    atexit.register(exit_handler)
    test_run = TestECG(input_num, api_url)
    asyncio.run(test_run.run())
