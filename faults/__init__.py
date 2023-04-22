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

    def empty_queue_calc_mean(self, q):
        total = 0
        count = 0
        if q.qsize() == 0:
            return 0
        else:
            while q.qsize() > 0:
                data = q.get()
                total += data
                count += 1
            return total / count

    def get_fan_status(self):
        return self.fan_status

    # this needs to run to assign fan status that other faults use
    def hi_fan_speed_check(self, motor_speed_data):
        motor_speed_mean = self.empty_queue_calc_mean(motor_speed_data)
        self.fan_status = True if motor_speed_mean > 0 else False
        return motor_speed_mean >= (
            self.fan_vfd_max_speed_err_thres_pv - self.fan_vfd_err_thres_pv
        )

    def low_duct_pressure_check(self, pressure_data, setpoint_data):
        pressure_mean = self.empty_queue_calc_mean(pressure_data)
        setpoint_mean = self.empty_queue_calc_mean(setpoint_data)
        return pressure_mean < (
            setpoint_mean - self.supply_air_static_pressure_err_thres_pv
        )

    def get_fault_one_data(self):
        motor_speed_data = self.fan_vfd_cache
        pressure_data = self.supply_air_static_pressure_cache
        setpoint_data = self.supply_air_static_pressure_setpoint_cache
        return pressure_data, setpoint_data, motor_speed_data

    def fault_check_condition_one(self):
        pressure_data, setpoint_data, motor_speed_data = self.get_fault_one_data()
        return self.low_duct_pressure_check(
            pressure_data, setpoint_data
        ) and self.hi_fan_speed_check(motor_speed_data)
        
    def get_fault_two_data(self):
        pass

    def fault_check_condition_two(self):
        return False
    
    def get_fault_three_data(self):
        pass

    def fault_check_condition_three(self):
        return False
    
    def get_fault_four_data(self):
        pass

    def fault_check_condition_four(self):
        return False
    
    def get_fault_five_data(self):
        pass

    def fault_check_condition_five(self):
        return False
    
    def get_fault_six_data(self):
        pass

    def fault_check_condition_six(self):
        return False
    
    def get_fault_seven_data(self):
        pass

    def fault_check_condition_seven(self):
        return False
    
    def get_fault_eight_data(self):
        pass

    def fault_check_condition_eight(self):
        return False
    
    def get_fault_nine_data(self):
        pass

    def fault_check_condition_nine(self):
        return False
    
    def get_fault_ten_data(self):
        pass

    def fault_check_condition_ten(self):
        return False
    
    def get_fault_eleven_data(self):
        pass

    def fault_check_condition_eleven(self):
        return None
    
    def get_fault_twelve_data(self):
        pass

    def fault_check_condition_twelve(self):
        return False
    
    def get_fault_thirteen_data(self):
        pass

    def fault_check_condition_thirteen(self):
        return False
    
    def get_fault_fourteen_data(self):
        pass

    def fault_check_condition_fourteen(self):
        return False
    
    def get_fault_fifteen_data(self):
        pass

    def fault_check_condition_fifteen(self):
        return False

