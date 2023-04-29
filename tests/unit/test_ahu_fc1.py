import pytest
from faults import FaultEquationOne, Cache

'''
to see print statements in pytest run with
$ pytest tests/unit/test_ahu_fc1.py -rP

duct static pressure low when fan at full speed
'''


@pytest.fixture
def fault_equation_one():
    fe_one = FaultEquationOne()
    fe_one.supply_air_static_pressure_err_thres_pv = 0.1
    fe_one.fan_vfd_max_speed_err_thres_pv = 100.0
    fe_one.fan_vfd_err_thres_pv = 5.0
    return fe_one

def test_fault_true(fault_equation_one):
    fault_equation_one.clear_caches()
    fault_equation_one.add_supply_air_static_pressure_data(0.4)
    fault_equation_one.add_supply_air_static_pressure_setpoint_data(1.0)
    fault_equation_one.add_fan_vfd_data(99.0)
    assert fault_equation_one.run_fault_check() == True

def test_fault_fan_off_false(fault_equation_one):
    fault_equation_one.clear_caches()
    fault_equation_one.add_supply_air_static_pressure_data(0.4)
    fault_equation_one.add_supply_air_static_pressure_setpoint_data(1.0)
    fault_equation_one.add_fan_vfd_data(0.0)
    assert fault_equation_one.run_fault_check() == False

def test_no_fault_false(fault_equation_one):
    fault_equation_one.clear_caches()
    fault_equation_one.add_supply_air_static_pressure_data(1.4)
    fault_equation_one.add_supply_air_static_pressure_setpoint_data(1.0)
    fault_equation_one.add_fan_vfd_data(99.0)
    assert fault_equation_one.run_fault_check() == False

