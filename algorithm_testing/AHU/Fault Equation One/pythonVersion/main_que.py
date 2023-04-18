import random
import time
import threading
import queue

# ASHRAE Guideline 36 fault detection parameters
VFD_SPEED_ERR_THRES = 0.05
VFD_SPEED_MAX_THRES = 0.99
PRESSURE_ERR_THRES = 0.1

# fake data parameters
pressure_low = 0.5
pressure_high = 1.5
setpoint_low = 1.0
setpoint_high = 1.4
motor_speed_low = 20.5
motor_speed_high = 95.5


class Machine:
    def __init__(self):
        self.pressure = None
        self.setpoint = None
        self.motor_speed = None

    def generate(self):
        self.pressure = round(random.uniform(pressure_low, pressure_high), 2)
        self.setpoint = round(random.uniform(setpoint_low, setpoint_high), 2)
        self.motor_speed = round(random.uniform(motor_speed_low, motor_speed_high), 2)


class DataGenerator:
    def __init__(self):
        self.pressure_data_storage = queue.Queue()
        self.setpoint_data_storage = queue.Queue()
        self.motor_speed_data_storage = queue.Queue()
        self.machine = Machine()
        self.second_count = 0

    def generate(self):
        while True:
            self.machine.generate()
            self.pressure_data_storage.put(self.machine.pressure)
            self.setpoint_data_storage.put(self.machine.setpoint)
            self.motor_speed_data_storage.put(self.machine.motor_speed)
            print(self.second_count)
            time.sleep(1)
            self.second_count += 1
            if self.second_count >= 300:
                self.second_count = 0

    def get_data(self):
        pressure_data = self.pressure_data_storage.get_nowait()
        setpoint_data = self.setpoint_data_storage.get_nowait()
        motor_speed_data = self.motor_speed_data_storage.get_nowait()
        return pressure_data, setpoint_data, motor_speed_data, self.pressure_data_storage, self.setpoint_data_storage, self.motor_speed_data_storage



class FaultDetector:
    def __init__(self, data_gen):
        self.data_gen = data_gen

    def empty_queue_calc_mean(self,queue_):
        total = 0
        count = 0
        while not queue_.empty():
            data = queue_.get()
            total += data
            count += 1
        if count > 0:
            average = total / count
        else:
            average = 0
        return average

    def pressure_check(self):
        pressure_data, setpoint_data, _, pressure_queue, setpoint_queue, _ = self.data_gen.get_data()
        pressure_queue.put(pressure_data)
        setpoint_queue.put(setpoint_data)
        pressure_mean = self.empty_queue_calc_mean(pressure_queue)
        setpoint_mean = self.empty_queue_calc_mean(setpoint_queue)
        return pressure_mean < (setpoint_mean - PRESSURE_ERR_THRES)


    def fan_check(self):
        _, _, motor_speed_data = self.data_gen.get_data()
        motor_speed_mean = self.empty_queue_calc_mean(motor_speed_data)
        return motor_speed_mean >= (VFD_SPEED_MAX_THRES - VFD_SPEED_ERR_THRES)

    def fault_check(self):
        if self.data_gen.pressure_data_storage.qsize() < 5:
            return False
        return self.pressure_check() and self.fan_check()


def main():
    data_gen = DataGenerator()
    fault_detector = FaultDetector(data_gen)
    data_sim_thread = threading.Thread(target=data_gen.generate)
    data_sim_thread.start()
    while True:
        print(f"FAULT DETECTION IS: {fault_detector.fault_check()}")
        time.sleep(300)


if __name__ == "__main__":
    main()
