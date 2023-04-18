import queue

class FaultDetector:
    def __init__(self):
        self.pressure_data_storage = queue.Queue()
        self.setpoint_data_storage = queue.Queue()
        self.motor_speed_data_storage = queue.Queue()
        
        self.vfd_err_thres = None
        self.vfd_max_speed_thres = None
        self.static_press_err_thres = None

    def get_data(self):
        pressure_data = self.pressure_data_storage
        setpoint_data = self.setpoint_data_storage
        motor_speed_data = self.motor_speed_data_storage
        return pressure_data, setpoint_data, motor_speed_data

    def empty_queue_calc_mean(self, queue_):
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

    def pressure_check(self, pressure_data, setpoint_data):
        pressure_mean = self.empty_queue_calc_mean(pressure_data)
        setpoint_mean = self.empty_queue_calc_mean(setpoint_data)
        return pressure_mean < (setpoint_mean - self.static_press_err_thres)
    
    def fan_check(self, motor_speed_data):
        motor_speed_mean = self.empty_queue_calc_mean(motor_speed_data)
        return motor_speed_mean >= (self.vfd_max_speed_thres - self.vfd_err_thres)

    def fault_check_condition_one(self):
        pressure_data, setpoint_data, motor_speed_data = self.get_data()
        return self.pressure_check(pressure_data, setpoint_data) and self.fan_check(motor_speed_data)
