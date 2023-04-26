#!/usr/bin/python

"""
Fault detection server app based on 
ASHRAE G36 for a VAV AHU
"""

# Standard library imports
from datetime import datetime

# Import fault logic
from faults import FaultEquationOne, FaultEquationTwo, Cache

# make the bacnet app
from bacnet_app import BacnetApp


# Third-party library imports
from bacpypes.core import run
from bacpypes.task import RecurringTask


# Constants
INTERVAL = 1.0


class DataSampler(RecurringTask):
    """
    A recurring task that runs fault detection every INTERVAL seconds.
    """

    def __init__(self, interval, device):
        """
        Initialize the DataSampler.

        Args:
            interval (float): The interval (in seconds) at which to run fault detection.
        """
        RecurringTask.__init__(self, interval * 1000)
        self.interval = interval
        self.device = device
        self.fd1_fault_last_value = "inactive"
        self.fd2_fault_last_value = "inactive"

        self.last_scan = datetime.now()
        self.fe_one = FaultEquationOne()
        self.fe_two = FaultEquationTwo()
        self.faults_to_check = [
            self.fe_one,
            self.fe_two
        ]

    def process_task(self):
        """
        FC1 equation add data to cache to process when 300 seconds expire
        """

        self.fe_one.add_supply_air_static_pressure_data(
            self.device.supply_air_static_pressure_av.presentValue
        )
        self.fe_one.add_supply_air_static_pressure_setpoint_data(
            self.device.supply_air_static_pressure_setpoint_av.presentValue
        )
        self.fe_one.add_fan_vfd_data(self.device.fan_vfd_av.presentValue)

        """
        FC2 equation add data to cache to process when 300 seconds expire
        """
        self.fe_two.add_mix_air_temp_data(
            self.device.mixed_air_temp_sensor_av.presentValue
        )
        self.fe_two.add_outside_air_temp_data(
            self.device.outside_air_temp_sensor_av.presentValue
        )
        self.fe_two.add_return_air_temp_data(
            self.device.return_air_temp_sensor_av.presentValue
        )

        """
        TODO FC3 and so on up to AHU rule 15
        """

        _now = datetime.now()
        last_scan_calc = abs(self.last_scan - _now).total_seconds()
        print(f"LAST SCAN CALC SECONDS is: {last_scan_calc}")

        # run G36 faults every 5 minutes
        if last_scan_calc < 300.0:
            return

        else:
            
            '''
            update current equation tuning parameters
            and then run the fault equations
            '''
            self.fe_one.supply_air_static_pressure_err_thres_pv = (
                self.device.supply_air_static_pressure_av.presentValue
            )
            self.fe_one.fan_vfd_max_speed_err_thres_pv = (
                self.device.fan_vfd_max_speed_err_thres_av.presentValue
            )
            self.fe_one.fan_vfd_err_thres_pv = (
                self.device.fan_vfd_err_thres_av.presentValue
            )
            
            self.fe_two.mix_air_temp_sensor_err_thres_pv = (
                self.device.air_temp_sensor_err_thres_av.presentValue
            )
            self.fe_two.outside_air_temp_sensor_err_thres_pv = (
                self.device.air_temp_sensor_err_thres_av.presentValue
            )
            self.fe_two.return_air_temp_sensor_err_thres_pv = (
                self.device.air_temp_sensor_err_thres_av.presentValue
            )            
            
            # loop thru each fault equation and run check
            for fault_rule in range(len(self.faults_to_check)):
                try:

                    in_fault = self.faults_to_check[fault_rule].run_fault_check()

                    print(f"fault_rule {fault_rule+1} is {in_fault}")

                    if fault_rule == 0:
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

                    elif fault_rule == 1:

                        # G36 FAULT LOGIC
                        if in_fault:
                            # change value of BV point
                            if self.fd2_fault_last_value == "inactive":
                                self.device.fault_condition_two_alarm_bv.presentValue = (
                                    "active"
                                )
                                self.fd2_fault_last_value = "active"
                                print(f"FC2 flag set to active!")
                        else:
                            # change value of BV point
                            if self.fd2_fault_last_value == "active":
                                self.device.fault_condition_two_alarm_bv.presentValue = (
                                    "inactive"
                                )
                                self.fd2_fault_last_value = "inactive"
                                print(f"FC2 flag set to inactive!")

                except Exception as e:
                    print(f"Error on {fault_rule} check! - {e}")
                    
            self.last_scan = datetime.now()

def main():
    app = BacnetApp()

    """BACnet discoverable points in app"""
    # TYPE,
    # POINT NAME,
    # DEFAULT PV,
    # DESCRIPTION
    point_tuples_in_brick_format = [
        # tuning params
        (
            "analogValue",
            "fan-vfd-err-thres",
            5.0,
            "Equation one tuning param the default is 5% motor speed command",
        ),
        (
            "analogValue",
            "fan-vfd-max-speed-err-thres",
            95.0,
            "Equation one tuning param the default is 95% motor speed command",
        ),
        (
            "analogValue",
            "supply-air-static-pressure-err-thres",
            0.1,
            "Equation one tuning param the default is 0.1 Inches WC. Use 25 for Pa.",
        ),
        (
            "analogValue",
            "air-temp-sensor-err-thres",
            2.0,
            "Tuning param for temperature sensors the default is 2 for °F. Use 1 for °C.",
        ),
        # sensor input
        (
            "analogValue",
            "supply-air-static-pressure",
            0.0,
            "Equation one input for supply air duct static pressure",
        ),
        (
            "analogValue",
            "supply-air-static-pressure-setpoint",
            0.0,
            "Equation one input for supply air duct static presure setpoint",
        ),
        (
            "analogValue",
            "fan-vfd",
            0.0,
            "Equation one input for supply fan motor vfd speed in percent",
        ),
        (
            "analogValue",
            "return-air-temp-sensor",
            0.0,
            "Equation two input for return air temperature",
        ),
        (
            "analogValue",
            "mixed-air-temp-sensor",
            0.0,
            "Equation two input for mixed air temperature",
        ),
        (
            "analogValue",
            "outside-air-temp-sensor",
            0.0,
            "Equation two input for outside air temperature",
        ),
        # fault alarm output
        (
            "binaryValue",
            "fault-condition-one-alarm",
            "inactive",
            "Equation one alarm supply fan is not meeting duct pressure setpoint",
        ),
        (
            "binaryValue",
            "fault-condition-two-alarm",
            "inactive",
            "Equation two alarm ix temp low; should be between out and return temp",
        ),
    ]

    app.make_app(point_tuples_in_brick_format)
    print("App made sucess!", app.bacnet_app)

    # checks server for data
    check_app_inputs_values = DataSampler(INTERVAL, app)
    check_app_inputs_values.install_task()

    run()


if __name__ == "__main__":
    main()
