from random import randrange, choice
from devices import SPO2Device, RRIDevice, TemperatureDevice, DeviceTypes
from apihandler import custom_senior_delete, custom_create_senior
from save_data import file_manager
from logger import Logger
import names
import time
import json


class Senior:
    def __init__(self, device, userdata):
        self.__name = userdata.get("name", None)
        self.__age = userdata.get("age", None)
        self.__room = userdata.get("room", None)
        self.__gender = userdata.get("gender", None)

        self.device = device
        self.id = device.id
        self.seq = 1
        self.last_data_update_time = 0

    def get_battery(self):
        return 60

    def get_data(self):
        return {
            "device_id": self.id,
            "time": int(time.time()),
            "value": self.device.get_value(),
            "battery": 60,
        }

    def __str__(self):
        return f"{self.__name}: {self.__age}, {self.id}, {self.__gender}"


class SeniorManager(Logger):
    def __init__(self):
        Logger.__init__(self, "SP")
        self.__senior_list = []

    def get_senior(self, count) -> list:
        senior_list = []
        data_list = file_manager.read_data(count)
        if len(data_list) == 0:
            return data_list
        # if len(data_list) == 0:
        #     self.info("No saved data, Creating new data")
        #     for i in range(count):
        #         senior = None
        #         while senior is None:
        #             senior = self.make_senior()
        #         senior_list.append(senior)
        else:
            self.info("Using saved data")
            for data in data_list:
                device = None
                device_id, device_type = data[:-1].split(',')
                device_type = DeviceTypes[device_type]

                if device_type == DeviceTypes.SPO2:
                    device = SPO2Device(device_id=device_id)
                elif device_type == DeviceTypes.RR:
                    device = RRIDevice(device_id=device_id)
                elif device_type == DeviceTypes.TEMP:
                    device = TemperatureDevice(device_id=device_id)

                senior = Senior(device, {"name": "_", "age": "_", "gender": "_", })
                senior_list.append(senior)

        return senior_list

    def make_senior(self, url):
        gender = choice(['male', 'female'])
        device = choice([RRIDevice, TemperatureDevice, SPO2Device])()  # Online RR_Device for now
        name = names.get_full_name(gender=gender)

        userdata = {
            "age": randrange(50, 100),
            "room_no": randrange(1, 200),
            "gender": gender,
            "name": name,
            "device_id": device.id,
            "device_type": device.type.name,
            "user": {
                "username": (name + str(randrange(0, 100))).replace(" ", ""),
                "email": f"{name}@gmail.com".replace(" ", ""),
                "password": "pass1234",
            },
        }

        res = custom_create_senior(json.dumps(userdata), url)
        if res is True:
            senior = Senior(device, userdata)
            file_manager.save_data(senior)
            self.info(senior)
            return senior
        else:
            self.error("Failed to create senior")
            return None

    def delete_senior(self, senior, url):
        custom_senior_delete(senior.id, url)


senior_manager = SeniorManager()
