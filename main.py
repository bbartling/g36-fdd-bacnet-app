#!/usr/bin/python

"""
Fault detection server app based on 
ASHRAE G36 for a VAV AHU
"""

# Standard library imports
from datetime import datetime

# Import fault logic
from faults import FaultDetector

# make the bacnet app
from bacnet_app import BacnetApp


# Third-party library imports
from bacpypes.core import run
from bacpypes.task import RecurringTask


# Constants
INTERVAL = 1.0


class FaultTasker(RecurringTask):
    """
    A recurring task that runs fault detection every INTERVAL seconds.
    """

    def __init__(self, interval, device):
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
        self.device = device
        self.faults_to_check = [
            "fault_check_condition_one",
            "fault_check_condition_two",
            "fault_check_condition_three",
            "fault_check_condition_four",
            "fault_check_condition_five",
            "fault_check_condition_six",
            "fault_check_condition_seven",
            "fault_check_condition_eight",
            "fault_check_condition_nine",
            "fault_check_condition_ten",
            "fault_check_condition_eleven",
            "fault_check_condition_twelve",
            "fault_check_condition_thirteen",
            "fault_check_condition_fourteen",
            "fault_check_condition_fifteen",
        ]

    def process_task(self):
        """
        Run fault detection.
        """
        self.fd.supply_air_static_pressure_cache.put(
            self.device.supply_air_static_pressure_av.presentValue
        )
        self.fd.supply_air_static_pressure_setpoint_cache.put(
            self.device.supply_air_static_pressure_setpoint_av.presentValue
        )
        self.fd.fan_vfd_cache.put(self.device.fan_vfd_av.presentValue)

        self.fd.fan_vfd_err_thres_pv = self.device.fan_vfd_err_thres_av.presentValue
        self.fd.fan_vfd_max_speed_err_thres_pv = (
            self.device.fan_vfd_max_speed_err_thres_av.presentValue
        )
        self.fd.supply_air_static_pressure_err_thres_pv = (
            self.device.supply_air_static_pressure_err_thres_av.presentValue
        )

        _now = datetime.now()
        last_scan_calc = abs(self.last_scan - _now).total_seconds()
        print(f"LAST SCAN CALC SECONDS is: {last_scan_calc}")
        
        '''
        # run G36 faults every 5 minutes
        if last_scan_calc < 30.0:
            return
        
        fault_condition = getattr(self.fd, "fault_check_condition_one")
        in_fault = fault_condition()
        
        print(f"fault_check_condition_one is {in_fault}")
        self.last_scan = datetime.now()
        '''

        # run G36 faults every 5 minutes
        if last_scan_calc < 300.0:
            return

        else:
            for fault_rule in self.faults_to_check:
                try:

                    fault_condition = getattr(self.fd, fault_rule)
                    in_fault = fault_condition()
                    
                    print(f"{fault_rule} is {in_fault}")

                    if fault_rule == "fault_check_condition_one":
                        # G36 FAULT LOGIC
                        if in_fault:
                            # change value of BV point
                            if self.fd1_fault_last_value == "inactive":
                                self.device.fault_condition_one_alarm_bv.presentValue = (
                                    "active"
                                )
                                self.fd1_fault_last_value = "active"
                                print(f"FC1 flag set to active!")
                        else:
                            # change value of BV point
                            if self.fd1_fault_last_value == "active":
                                self.device.fault_condition_one_alarm_bv.presentValue = (
                                    "inactive"
                                )
                                self.fd1_fault_last_value = "inactive"
                                print(f"FC1 flag set to inactive!")
                                
                except Exception as e:
                    print(f"Error on {fault_rule} check! - {e}")

            self.last_scan = datetime.now()
            
    

def main():
    app = BacnetApp()
    
    # BACnet discoverable points in app
    # TYPE, POINT NAME, DEFAULT PV, DESCRIPTION
    point_tuples_in_brick_format = [
        ("analogValue", "fan-vfd-err-thres", 5.0, "Default is 5%"),
        ("analogValue", "fan-vfd-max-speed-err-thres", 95.0, "Default is 95%"),
        ("analogValue", "supply-air-static-pressure-err-thres", 0.1, "Default is 0.1 Inches WC. Use 25 for Pa."),
        ("analogValue", "supply-air-static-pressure", 0.0, "Input for duct static pressure"),
        ("analogValue", "supply-air-static-pressure-setpoint", 0.0, "Input for duct static presure setpoint"),
        ("analogValue", "fan-vfd", 0.0, "Input for fan vfd speed in percent"),
        ("binaryValue", "fault-condition-one-alarm", "inactive", "Supply fan is not meeting duct pressure setpoint"),
    ]

    app.make_app(point_tuples_in_brick_format)
    print("App made sucess!", app.bacnet_app)

    # checks server for data
    check_app_inputs_values = FaultTasker(INTERVAL, app)
    check_app_inputs_values.install_task()

    run()


if __name__ == "__main__":
    main()
