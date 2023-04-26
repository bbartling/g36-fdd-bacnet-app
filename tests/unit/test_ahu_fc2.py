import pytest
from faults import FaultEquationTwo

'''
to see print statements in pytest run with
$ pytest tests/unit/test_ahu_fc2.py -rP

mix air temp lower should be between out and return
'''


@pytest.fixture
def fault_equation_two():
    fe_two = FaultEquationTwo()
    fe_two.mix_air_temp_sensor_err_thres_pv = 2.0
    fe_two.outside_air_temp_sensor_err_thres_pv = 2.0
    fe_two.return_air_temp_sensor_err_thres_pv = 2.0
    return fe_two

def test_fault_true(fault_equation_two):
    fault_equation_two.clear_caches()
    fault_equation_two.add_mix_air_temp_data(44.4)
    fault_equation_two.add_outside_air_temp_data(77.0)
    fault_equation_two.add_return_air_temp_data(55.0)
<<<<<<< HEAD
    assert fault_equation_two.fault_check_condition() == True
=======
    assert fault_equation_two.run_fault_check() == True
>>>>>>> fa8013851c6e329af4174ef1db9c7a10ce2a184e

def test_fault_false(fault_equation_two):
    fault_equation_two.clear_caches()
    fault_equation_two.add_mix_air_temp_data(66.4)
    fault_equation_two.add_outside_air_temp_data(77.0)
    fault_equation_two.add_return_air_temp_data(55.0)
<<<<<<< HEAD
    assert fault_equation_two.fault_check_condition() == False
=======
    assert fault_equation_two.run_fault_check() == False
>>>>>>> fa8013851c6e329af4174ef1db9c7a10ce2a184e

