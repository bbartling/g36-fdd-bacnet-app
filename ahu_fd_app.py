#!/usr/bin/python

"""
Fault detection server app based on 
ASHRAE G36 for a VAV AHU
"""

# Standard library imports
from datetime import datetime
from collections import deque

# Third-party library imports
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import run
from bacpypes.task import RecurringTask
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import BinaryValueObject, register_object_type
from bacpypes.local.device import LocalDeviceObject
from bacpypes.local.object import AnalogValueCmdObject

# Constants
INTERVAL = 1.0

# Register object type
register_object_type(AnalogValueCmdObject, vendor_id=999)

class FaultTasker(RecurringTask):
    """
    A recurring task that runs fault detection every INTERVAL seconds.
    """
    def __init__(self, interval):
        """
        Initialize the FaultTasker.

        Args:
            interval (float): The interval (in seconds) at which to run fault detection.
        """
        RecurringTask.__init__(self, interval * 1000)
        self.interval = interval
        self.fd1_fault_last_value = "inactive"
        self.last_scan = datetime.now()
        self.fd = FaultDetector()


    def process_task(self):
        """
        Run fault detection.
        """
        self.fd.pressure_data_storage.append(pressure_input_av.presentValue)
        self.fd.setpoint_data_storage.append(pressure_setpoint_input_av.presentValue)
        self.fd.motor_speed_data_storage.append(fan_speed_input_av.presentValue)
        
        _now = datetime.now()
        last_scan_calc = abs(self.last_scan - _now).total_seconds()
        print(f"LAST SCAN CALC SECONDS is: {last_scan_calc}")

        # run G36 faults every 5 minutes
        if last_scan_calc < 300.0:
            return
        
        else:
            try:
                fc1_fault = self.fd.fault_check_condition_one()
                
                # G36 FAULT LOGIC 
                if fc1_fault:
                    # change value of BV point
                    if self.fd1_fault_last_value == "inactive":
                        fault_output_bv.presentValue = "active"
                        self.fd1_fault_last_value = "active"
                        print(f'FC1 flag set to active!')
                else:
                    # change value of BV point
                    if self.fd1_fault_last_value == "active":
                        fault_output_bv.presentValue = "inactive"
                        self.fd1_fault_last_value = "inactive"
                        print(f'FC1 flag set to inactive!')
            except Exception as e:
                print(f'Error on FC1 check! - {e}')
        
            self.last_scan = datetime.now()

        

class FaultDetector:
    def __init__(self):
        self.pressure_data_storage = deque(maxlen=1000)
        self.setpoint_data_storage = deque(maxlen=1000)
        self.motor_speed_data_storage = deque(maxlen=1000)

    def get_data(self):
        pressure_data = self.pressure_data_storage[-300:]
        setpoint_data = self.setpoint_data_storage[-300:]
        motor_speed_data = self.motor_speed_data_storage[-300:]
        return pressure_data, setpoint_data, motor_speed_data

    def pressure_check(self):
        pressure_data, setpoint_data, _ = self.get_data()
        pressure_mean = sum(pressure_data) / len(pressure_data)
        setpoint_mean = sum(setpoint_data) / len(setpoint_data)
        return pressure_mean < (setpoint_mean - static_press_err_thres.presentValue)

    def fan_check(self):
        _, _, motor_speed_data = self.get_data()
        motor_speed_mean = sum(motor_speed_data) / len(motor_speed_data)
        return motor_speed_mean >= (vfd_max_speed_thres.presentValue - vfd_err_thres.presentValue)

    def fault_check_condition_one(self):
        if len(self.pressure_data_storage) < 300:
            return False
        return self.pressure_check() and self.fan_check()
        

def main():
    global pressure_input_av, pressure_setpoint_input_av, fan_speed_input_av, \
        fault_output_bv, fault_detector_application, vfd_err_thres, \
        vfd_max_speed_thres, static_press_err_thres

    # make a parser
    parser = ConfigArgumentParser(description=__doc__)

    # parse the command line arguments
    args = parser.parse_args()

    # make a device object
    this_device = LocalDeviceObject(ini=args.ini)

    # make fault detection application
    fault_detector_application = BIPSimpleApplication(this_device, args.ini.address)

    # make an analog value object
    vfd_err_thres = AnalogValueCmdObject(
        objectIdentifier=("analogValue", 1),
        objectName="Fan-VFD-Error-Threshold",
        presentValue=5.0,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
    )

    # add it to the device
    fault_detector_application.add_object(vfd_err_thres)

    # make an analog value object
    vfd_max_speed_thres = AnalogValueCmdObject(
        objectIdentifier=("analogValue", 2),
        objectName="Fan-VFD-Max-Speed-Threshold",
        presentValue=95.0,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
    )

    # add it to the device
    fault_detector_application.add_object(vfd_max_speed_thres)
    
    # make an analog value object
    static_press_err_thres = AnalogValueCmdObject(
        objectIdentifier=("analogValue", 3),
        objectName="Static-Press-Error-Threshold",
        presentValue=0.1,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
    )

    # add it to the device
    fault_detector_application.add_object(static_press_err_thres)

    # make an analog value object
    pressure_input_av = AnalogValueCmdObject(
        objectIdentifier=("analogValue", 4),
        objectName="Static-Pressure-Input",
        presentValue=0.0,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
    )

    # add it to the device
    fault_detector_application.add_object(pressure_input_av)
    
    # make an analog value object
    pressure_setpoint_input_av = AnalogValueCmdObject(
        objectIdentifier=("analogValue", 5),
        objectName="Static-Pressure-Setpoint-Input",
        presentValue=0.0,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
    )

    # add it to the device
    fault_detector_application.add_object(pressure_setpoint_input_av)
    
    # make an analog value object
    fan_speed_input_av = AnalogValueCmdObject(
        objectIdentifier=("analogValue", 6),
        objectName="Supply-Fan-Speed-Input",
        presentValue=0.0,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
    )

    # add it to the device
    fault_detector_application.add_object(fan_speed_input_av)
    
    # make a binary value object
    fault_output_bv = BinaryValueObject(
        objectIdentifier=("binaryValue", 7),
        objectName="Fault-Condition-One-Alarm",
        presentValue="inactive",
        statusFlags=[0, 0, 0, 0],
    )

    # add it to the device
    fault_detector_application.add_object(fault_output_bv)

    # binary value task
    do_something_task = FaultTasker(INTERVAL)
    do_something_task.install_task()
    

    run()


if __name__ == "__main__":
    main()

