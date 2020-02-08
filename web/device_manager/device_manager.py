#!/usr/bin/python3

import time
import json
import random
import logging
import datetime
import threading
from RF24 import *
import RPi.GPIO as GPIO

try:
    from django.utils import timezone
    _g__gettime = timezone
    _g__gettime.now()
except:
    _g__gettime = datetime.datetime

log_filename = '/home/pi/device_manager.log'
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

DEFAULT_PIPE_A = 0xC2C2C2C2C2
DEFAULT_PIPE_B = 0xE2E2E2E2E2

class RadioManager(object):

    def __init__(self):
        self._radio = None
        self._pipe_a = 0
        self._pipe_b = 1
        self._data_buffer = 0
        self._data_buffer_size = 30
    
    def initialize(self, radio=RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ), pipe_a=DEFAULT_PIPE_A, pipe_b=DEFAULT_PIPE_B):
        self._radio = radio
        self._pipe_a = pipe_a
        self._pipe_b = pipe_b

        self._radio.begin()
        self._radio.setChannel(90)
        self._radio.setPALevel(RF24_PA_MAX)
        self._radio.setDataRate(RF24_1MBPS)
        self._radio.setAutoAck(1)
        self._radio.setRetries(2, 15)
        self._radio.setCRCLength(RF24_CRC_8)

        self._radio.powerUp()

    def terminate(self):
        self._radio.stopListening()
        self._radio.powerDown()

    def transfer(self, data):
        return self.transfer_to_pipe(data, self._pipe_a, self._pipe_b)
    
    def transfer_to_pipe(self, data, pipe_a, pipe_b):
        if not isinstance(data, str):
            return False

        self._radio.openWritingPipe(pipe_b)
        self._radio.openReadingPipe(1, pipe_a)
        self._radio.stopListening()

        err_code = 0 if self._radio.writeFast(data, min(len(data), self._data_buffer_size)) else -1

        self._radio.txStandBy()
        self._radio.stopListening()

        return err_code

    def receive(self, howmany, timeout_s):
        return self.read_from_pipe(howmany, timeout_s, self._pipe_a, self._pipe_b)
    
    def read_from_pipe(self, howmany, timeout_s, pipe_a, pipe_b):
        self._radio.openWritingPipe(pipe_a)
        self._radio.openReadingPipe(1, pipe_b)
        self._radio.startListening()

        err_code = 0
        start_time = time.time()

        while True:
            if time.time() - start_time >= timeout_s:
                err_code = -1
                break
            
            if self._radio.available():
                self._data_buffer = self._radio.read(howmany)
                break

        self._radio.stopListening()

        return err_code

    def get_databuffer(self):
        return self._data_buffer

    def print_details(self):
        self._radio.printDetails()

class Device(object):
    def __init__(self, name="device", idIn=0):
        self.id = idIn
        self.name = name

        self.__pipe_a = None
        self.__pipe_b = None

        self.__user = None
        self.__state = False
        self.__time_on = _g__gettime.now() #datetime.datetime.now()
        self.__time_off = _g__gettime.now()
        self.__total_time = self.__time_off - self.__time_on

        self.__state_change_callbacks = dict()
        self.thread_pool = []
    
    def __repr__(self):
        return "Device({})".format(self.__str__())
    
    def __str__(self):
        res = {
            "name" : self.name,
            "user" : self.__user,
            "state" : self.__state,
            "pipe_a" : self.__pipe_a,
            "pipe_b" : self.__pipe_b,
            "time_on" : self.__time_on,
            "time_off" : self.__time_off,
            "total_time" : self.__total_time,
        }

        return json.dumps(res)

    def __hash__(self):
        return hash(self.__str__())

    def initialize(self, pipe_a=DEFAULT_PIPE_A, pipe_b=DEFAULT_PIPE_B):
        self.__pipe_a = pipe_a
        self.__pipe_b = pipe_b

    def terminate(self):
        self.__pipe_a = None
        self.__pipe_b = None
    
    def update(self, radio_manager):
        if radio_manager.read_from_pipe(4, 2, self.__pipe_a, self.__pipe_b) != 0:
            return False

        logging.debug("Received message from device")

        try:
            d = str(radio_manager.get_databuffer().decode("utf-8"))
        except:
            return

        logging.debug("d: {}".format(d))

        if not (d.startswith("{") and d.endswith("}")):
            return False
        
        logging.debug("setting state; u: {}, s: {}".format(int(d[2]), int(d[1])))
        self.set_state(user=int(d[2]), state=int(d[1]))
        return True
    
    def add_state_change_callback(self, tag, callback):
        if not callable(callback):
            return False

        if tag in self.__state_change_callbacks.values():
            raise ValueError("Invaild tag: Tag `{}` exists.".format(tag))

        self.__state_change_callbacks[tag] = callback
        return True

    def remove_state_change_callback(self, tag):
        if tag not in self.__state_change_callbacks.keys():
            raise ValueError("Invaild tag: Tag `{}` does not exist.".format(tag))
        
        self.__state_change_callbacks.pop(tag)
    
    def get_state(self):
        return self.__state

    def set_state(self, user, state):

        if self.__state == state and self.__user == user:
            return

        current_time = _g__gettime.now() #datetime.datetime.now()

        # handle case when device remains on -- but switches user
        if self.__state and self.__user != user:
            self.__state = 0 # turn off for previous user
            self.__time_off = current_time
            self.__total_time = self.__time_off - self.__time_on

            self.do_callbacks()
        
        # handle case when device remains off -- but switches user
        if (not state) and self.__user != user:
            return
        
        self.__user = user
        self.__state = state

        if self.__state:
            self.__time_on = _g__gettime.now() #datetime.datetime.now()
        else:
            self.__time_off = _g__gettime.now() #datetime.datetime.now()
            self.__total_time = self.__time_off - self.__time_on
        
        self.do_callbacks()

    def do_callbacks(self):
        for callback in self.__state_change_callbacks.values():
            if not callable(callback):
                continue

            self.thread_pool.append(
                threading.Thread(target=callback, args=(self,))
            )
            self.thread_pool[-1].start()
    
    def get_state(self):
        return self.__state
    
    def get_user(self):
        return self.__user
    
    def get_timestamp(self):
        res = {
            "time_on" : self.__time_on,
            "time_off" : self.__time_off,
            "total_time" : self.__total_time,
        }

        return res
    
    def get_pipes(self):
        res = {
            "pipe_a" : self.__pipe_a,
            "pipe_b" : self.__pipe_b,
        }

        return res


class DeviceManager(object):
    def __init__(self):
        self.__radio_manager = None
        self.__devices = dict()
        
        self.__should_run = False

    def initialize(self, radio=RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ)):
        self.set_radio(radio)
        self.__should_run = True

        logging.debug("initialized radio")

    def terminate(self):
        self.kill()

        self.__radio_manager.terminate()
        self.__radio_manager = None
    
    def clear_devices(self):
        self.__devices = dict()
    
    def kill(self):
        self.__should_run = False
        time.sleep(1)

    def print_details(self):
        self.__radio_manager.print_details()

    def set_radio(self, radio):
        if not (self.__radio_manager is None):
            self.__radio_manager.terminate()

        self.__radio_manager = RadioManager()
        self.__radio_manager.initialize(radio=radio)
    
    def add_device(self, tag, device):
        if tag in self.__devices.keys():
            raise ValueError("Tag Error: Tag `{}` exists".format(tag))
        
        logging.debug("added device with tag: {}".format(tag))
        self.__devices[tag] = device
    
    def remove_device(self, tag):
        if tag not in self.__devices.keys():
            raise ValueError("Tag Error: Tag `{}` does not exist".format(tag))

        logging.debug("removed device with tag: {}".format(tag))
        self.__devices.pop(tag)
    
    def update(self):
        for device in self.__devices.values():
            device.update(self.__radio_manager)
        
    def run(self, block=False, loop_interval=0.5):

        def __thread(interval):
            logging.debug("started run thread")
            
            while self.__should_run:
                self.update()
                time.sleep(interval)
            
            logging.debug("exited run thread")
        
        self.thread = threading.Thread(target=__thread, args=(loop_interval,))
        self.thread.start()

        if block:
            self.thread.join()

if __name__ == "__main__":
    device_manager = DeviceManager()
    device_manager.initialize()
    device_manager.print_details()

    device_1 = Device("Device 1")
    device_2 = Device("Device 2")

    device_1.initialize(pipe_a=0x0111111111, pipe_b=0x1111111111)
    device_2.initialize(pipe_a=0x0222222222, pipe_b=0x1222222222)

    def callback_function(device):
        if device.get_state():
            print ("{} is ON".format(device.name))
        else:
            print ("{} is OFF".format(device.name))

    device_1.add_state_change_callback("test", callback_function)
    device_2.add_state_change_callback("test", callback_function)
    
    device_manager.add_device("device_1", device_1)
    device_manager.add_device("device_2", device_2)

    device_manager.run(block=True)
    device_manager.terminate()
