import pytest
from faults import FaultDetector

'''
to see print statements in pytest run with
$ pytest tests/unit/test_ahu_fc1.py -rP

duct static pressure low when fan at full speed
'''

@pytest.fixture
def fault_detector():
    return FaultDetector()


def test_fault_check_condition_one_true(fault_detector):
    # blantently obvious fan in fault
    pressure_data = 0.4
    setpoint_data = 1.0
    motor_speed_data = 99.0
    
    fault_detector.fan_vfd_err_thres_pv = 5.0
    fault_detector.fan_vfd_max_speed_err_thres_pv = 95.0
    fault_detector.supply_air_static_pressure_err_thres_pv = 0.1

    fault_detector.supply_air_static_pressure_cache.put(pressure_data)
    fault_detector.supply_air_static_pressure_setpoint_cache.put(setpoint_data)
    fault_detector.fan_vfd_cache.put(motor_speed_data)

    assert fault_detector.fault_check_condition_one() == True



def test_fault_check_condition_one_false(fault_detector):
    # blantently obvious fan in fault
    pressure_data = 0.99
    setpoint_data = 1.0
    motor_speed_data = 44.0
    
    fault_detector.fan_vfd_err_thres_pv = 5.0
    fault_detector.fan_vfd_max_speed_err_thres_pv = 95.0
    fault_detector.supply_air_static_pressure_err_thres_pv = 0.1

    fault_detector.supply_air_static_pressure_cache.put(pressure_data)
    fault_detector.supply_air_static_pressure_setpoint_cache.put(setpoint_data)
    fault_detector.fan_vfd_cache.put(motor_speed_data)

    assert fault_detector.fault_check_condition_one() == False