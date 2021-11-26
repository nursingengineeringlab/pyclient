import os
from random import random
import binascii
import enum

Device_Description = {
    "RRI": {
        "id": 1,
        "watch_threshold_min": 600,
        "watch_threshold_max": 1200,
        "trigger_min_direction": [700, 650, 550],
        "trigger_max_direction": [1000, 1100, 1200],
    },
    "TEMP": {
        "id": 2,
        "watch_threshold_min": 97,
        "watch_threshold_max": 99.5,
        "trigger_min_direction": [97, 96.5, 96],
        "trigger_max_direction": [99.5, 100.0, 100.9],
    },
    "SPO2": {
        "id": 3,
        "watch_threshold_min": 95,
        "watch_threshold_max": 99.5,
        "trigger_min_direction": [95, 93, 90],
        "trigger_max_direction": [100, 100.0, 100],
    },
}


class DeviceTypes(enum.Enum):
    ECG = 1
    RRI = 2
    TEMP = 3
    SPO2 = 4


class Device:
    def __init__(self, id, mtype, noise_amplitude=1):
        self.type = mtype
        self.lower = Device_Description[self.type.name]["watch_threshold_min"]
        self.higher = Device_Description[self.type.name]["watch_threshold_max"]
        self.id = id if id else binascii.hexlify(bytearray(os.urandom(6))).decode('ascii').upper()
        self.value = (self.lower + self.higher) / 2
        self.noise_amplitude = noise_amplitude

    def get_value(self):
        noise = random() * 2 - 1  # generate random noise from -1 to 1
        self.value = round(self.value + (noise * self.noise_amplitude), 2)
        return self.value


class RRIDevice(Device):
    def __init__(self, device_id=None):
        Device.__init__(self, device_id, DeviceTypes.RRI, noise_amplitude=10)


class TemperatureDevice(Device):
    def __init__(self, device_id=None):
        Device.__init__(self, device_id, DeviceTypes.TEMP, noise_amplitude=0.5)


class SPO2Device(Device):
    def __init__(self, device_id=None):
        Device.__init__(self, device_id, DeviceTypes.SPO2, noise_amplitude=1)
