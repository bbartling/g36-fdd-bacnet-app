import pytest
from faults import FaultDetector

'''
to see print statements in pytest run with
$ pytest tests/unit/test_ahu_fc2.py -rP

mix air temp lower should be between out and return
'''

@pytest.fixture
def fault_detector():
    return FaultDetector()



def test_fault_check_condition_two_true(fault_detector):
    # blantently obvious mix air temp lower than out temp
    
    mix_air_temp_data = 33.0
    outside_air_temp_data = 66.0
    return_air_temp_data = 55.0

    fault_detector.fan_status = True
    fault_detector.mixed_air_temp_sensor_err_thres_pv = 2.0
    fault_detector.outside_air_temp_sensor_err_thres_pv = 2.0
    fault_detector.return_air_temp_sensor_err_thres_pv = 2.0

    fault_detector.mixed_air_temp_sensor_cache.put(mix_air_temp_data)
    fault_detector.outside_air_temp_sensor_cache.put(outside_air_temp_data)
    fault_detector.return_air_temp_sensor_cache.put(return_air_temp_data)

    assert fault_detector.fault_check_condition_two() == True



def test_fault_check_condition_two_false(fault_detector):
    # blantently obvious mix air temp in good range
    
    mix_air_temp_data = 60.0
    outside_air_temp_data = 66.0
    return_air_temp_data = 55.0

    fault_detector.fan_status = True
    fault_detector.mixed_air_temp_sensor_err_thres_pv = 2.0
    fault_detector.outside_air_temp_sensor_err_thres_pv = 2.0
    fault_detector.return_air_temp_sensor_err_thres_pv = 2.0

    fault_detector.mixed_air_temp_sensor_cache.put(mix_air_temp_data)
    fault_detector.outside_air_temp_sensor_cache.put(outside_air_temp_data)
    fault_detector.return_air_temp_sensor_cache.put(return_air_temp_data)

    assert fault_detector.fault_check_condition_two() == False


def test_fault_check_condition_two_false_fan_off(fault_detector):
    # mix temp in range but fan is off
    
    mix_air_temp_data = 60.0
    outside_air_temp_data = 66.0
    return_air_temp_data = 55.0

    fault_detector.fan_status = False
    fault_detector.mixed_air_temp_sensor_err_thres_pv = 2.0
    fault_detector.outside_air_temp_sensor_err_thres_pv = 2.0
    fault_detector.return_air_temp_sensor_err_thres_pv = 2.0

    fault_detector.mixed_air_temp_sensor_cache.put(mix_air_temp_data)
    fault_detector.outside_air_temp_sensor_cache.put(outside_air_temp_data)
    fault_detector.return_air_temp_sensor_cache.put(return_air_temp_data)

    assert fault_detector.fault_check_condition_two() == False