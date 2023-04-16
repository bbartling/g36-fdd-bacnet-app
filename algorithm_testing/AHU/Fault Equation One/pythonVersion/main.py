import random
import time
import threading

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
        self.pressure_data_storage = []
        self.setpoint_data_storage = []
        self.motor_speed_data_storage = []
        self.machine = Machine()

    def generate(self):
        while True:
            self.machine.generate()
            self.pressure_data_storage.append(self.machine.pressure)
            self.setpoint_data_storage.append(self.machine.setpoint)
            self.motor_speed_data_storage.append(self.machine.motor_speed)
            print(time.ctime())
            time.sleep(1)

    def get_data(self):
        pressure_data = self.pressure_data_storage[-300:]
        setpoint_data = self.setpoint_data_storage[-300:]
        motor_speed_data = self.motor_speed_data_storage[-300:]
        return pressure_data, setpoint_data, motor_speed_data


class FaultDetector:
    def __init__(self, data_gen):
        self.data_gen = data_gen

    def pressure_check(self):
        pressure_data, setpoint_data, _ = self.data_gen.get_data()
        pressure_mean = sum(pressure_data) / len(pressure_data)
        setpoint_mean = sum(setpoint_data) / len(setpoint_data)
        return pressure_mean < (setpoint_mean - PRESSURE_ERR_THRES)

    def fan_check(self):
        _, _, motor_speed_data = self.data_gen.get_data()
        motor_speed_mean = sum(motor_speed_data) / len(motor_speed_data)
        return motor_speed_mean >= (VFD_SPEED_MAX_THRES - VFD_SPEED_ERR_THRES)

    def fault_check(self):
        if len(self.data_gen.pressure_data_storage) < 300:
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
