import queue


class FaultDetector:
    def __init__(self):
        self.supply_air_static_pressure_cache = queue.Queue()
        self.supply_air_static_pressure_setpoint_cache = queue.Queue()
        self.fan_vfd_cache = queue.Queue()

        self.fan_vfd_err_thres_pv = None
        self.fan_vfd_max_speed_err_thres_pv = None
        self.supply_air_static_pressure_err_thres_pv = None
        
        self.fan_status = None

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
    
    def calc_fan_status(self):
        motor_speed_data = self.fan_vfd_cache
        motor_speed_mean = self.empty_queue_calc_mean(motor_speed_data)
        self.fan_status = motor_speed_mean >= (
            self.fan_vfd_max_speed_err_thres_pv - self.fan_vfd_err_thres_pv
        )
        
    def fan_check(self):
        return self.fan_status
    
    def pressure_check(self, pressure_data, setpoint_data):
        pressure_mean = self.empty_queue_calc_mean(pressure_data)
        setpoint_mean = self.empty_queue_calc_mean(setpoint_data)
        return pressure_mean < (
            setpoint_mean - self.supply_air_static_pressure_err_thres_pv
        )
    
    def get_data_fault_one(self):
        pressure_data = self.supply_air_static_pressure_cache
        setpoint_data = self.supply_air_static_pressure_setpoint_cache
        return pressure_data, setpoint_data, self.fan_status

    def fault_check_condition_one(self):
        pressure_data, setpoint_data, fan_status = self.get_data_fault_one()
        return self.pressure_check(pressure_data, setpoint_data) and fan_status
    
    def fault_check_condition_two(self):
        return False
    
    def fault_check_condition_three(self):
        return False
    
    def fault_check_condition_four(self):
        return False
    
    def fault_check_condition_five(self):
        return False
    
    def fault_check_condition_six(self):
        return False
    
    def fault_check_condition_seven(self):
        return False
    
    def fault_check_condition_eight(self):
        return False
    
    def fault_check_condition_nine(self):
        return False
    
    def fault_check_condition_ten(self):
        return False
    
    def fault_check_condition_eleven(self):
        return None
    
    def fault_check_condition_twelve(self):
        return False
    
    def fault_check_condition_thirteen(self):
        return False
    
    def fault_check_condition_fourteen(self):
        return False
    
    def fault_check_condition_fifteen(self):
        return False