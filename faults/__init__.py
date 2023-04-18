


class FaultDetector:
    def __init__(self):
        self.pressure_data_storage = queue.Queue()
        self.setpoint_data_storage = queue.Queue()
        self.motor_speed_data_storage = queue.Queue()

    def get_data(self):
        pressure_data = self.pressure_data_storage.get_nowait()
        setpoint_data = self.setpoint_data_storage.get_nowait()
        motor_speed_data = self.motor_speed_data_storage.get_nowait()
        return pressure_data, setpoint_data, motor_speed_data

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
        pressure_data, setpoint_data, _, pressure_queue, setpoint_queue, _ = self.get_data()
        pressure_queue.put(pressure_data)
        setpoint_queue.put(setpoint_data)
        pressure_mean = self.empty_queue_calc_mean(pressure_queue)
        setpoint_mean = self.empty_queue_calc_mean(setpoint_queue)
        return pressure_mean < (setpoint_mean - PRESSURE_ERR_THRES)
    
    def fan_check(self):
        _, _, motor_speed_data = self.get_data()
        motor_speed_mean = self.empty_queue_calc_mean(motor_speed_data)
        return motor_speed_mean >= (VFD_SPEED_MAX_THRES - VFD_SPEED_ERR_THRES)

    def fault_check_condition_one(self):
        if self.pressure_data_storage.qsize() < 5:
            print("not enough data to run FDD!")
            return False

        return self.pressure_check() and self.fan_check()
