"""
Agent documentation goes here.
"""

__docformat__ = "reStructuredText"

import logging
import sys
import operator
import pandas as pd
import numpy as np
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC
from volttron.platform.messaging import topics, headers

from faultmachine import FaultConditionOne, FaultConditionTwo

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


# for each AHU as defined by config file
class AhuSystem:
    pass


def faultmachine(config_path, **kwargs):
    """
    Parses the Agent configuration and returns an instance of
    the agent created using that configuration.

    :param config_path: Path to a configuration file.
    :type config_path: str
    :returns: Faultmachine
    :rtype: Faultmachine
    """
    try:
        config = utils.load_config(config_path)
        _log.info(f"[G36 Agent INFO] -  config Load SUCCESS")
    except Exception:
        _log.info(f"[G36 Agent INFO] -  config Load FAIL")

        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    return Faultmachine(**kwargs)


class Faultmachine(Agent):
    """
    Document agent constructor here.
    """

    def __init__(self, **kwargs):
        super(Faultmachine, self).__init__(**kwargs)
        _log.info("vip_identity: " + self.core.identity)

        self.default_config = {}

        # Set a default configuration to ensure that self.configure is called immediately to setup
        # the agent.
        self.vip.config.set_default("config", self.default_config)
        # Hook self.configure up to changes to the configuration file "config".
        self.vip.config.subscribe(
            self.configure, actions=["NEW", "UPDATE"], pattern="config"
        )

        self.ahus_as_a_class = []

        # G36 default FC1 params for the FDD algorithm
        self.vfd_speed_percent_err_thres = 0.05
        self.duct_static_inches_err_thres = 0.99
        self.vfd_speed_percent_max = 0.1

        # G36 default FC2 params
        self.mix_degf_err_thres = 5.0
        self.return_degf_err_thres = 5.0
        self.outdoor_degf_err_thres = 2.0

    def configure(self, config_name, action, contents):
        """
        Called after the Agent has connected to the message bus. If a configuration exists at startup
        this will be called before onstart.

        Is called every time the configuration in the store changes.
        """
        config = self.default_config.copy()
        config.update(contents)

        _log.info("[G36 Agent INFO] - Configuring Agent")

        device_num_init = 0
        device_num = device_num_init

        try:
            _log.info(f"[G36 Agent INFO] - {config}")

            for ahu, device_attributes in config.items():
                # _log.info(f"device: {device}")
                # _log.info(f"device_attributes: {device_attributes}")

                device_num = AhuSystem()
                self.ahus_as_a_class.append(device_num)

                variables = device_attributes[0].get("variables")
                device = device_attributes[0].get("device")
                topic = device_attributes[0].get("topic")

                for variable, point_name in variables[0].items():
                    setattr(device_num, variable, point_name)

                # create empty lists in the class
                # and append new data from info on msg bus
                
                # fc 1 equation input
                setattr(device_num, "duct_static_setpoint_data", list())
                setattr(device_num, "duct_static_data", list())
                setattr(device_num, "vfd_speed_data", list())
                
                # fc 1 equation input
                setattr(device_num, "mixing_air_temp_data", list())
                setattr(device_num, "outdoor_air_temp_data", list())
                setattr(device_num, "return_air_temp_data", list())
                
                
                '''
                setattr(device_num, "cooling_valve_data", list())
                setattr(device_num, "heating_valve_data", list())
                setattr(device_num, "mixing_dampers_data", list())
                setattr(device_num, "supply_air_volume_data", list())
                setattr(device_num, "supply_air_pressure_data", list())
                setattr(device_num, "supply_air_pressure_setpoint_data", list())
                setattr(device_num, "supply_air_temp_data", list())
                setattr(device_num, "supply_air_temp_setpoint_data", list())
                '''


                _log.info(f"[G36 Agent INFO] - Configs Set Success for {ahu}")

                subscription_prefix = f"devices/{topic}/{device}/"
                _log.info(f"[G36 Agent INFO] - subscribe to: {subscription_prefix}")

                # subscribe to this device
                self.vip.pubsub.subscribe(
                    peer="pubsub",
                    prefix=subscription_prefix,
                    callback=self._handle_publish,
                )

                device_num_init += 1

                _log.info(
                    f"[G36 Agent INFO] - Subscribition Success on device: {device}!!"
                )

        except ValueError as e:
            _log.error(
                "[G36 Agent INFO] - ERROR PROCESSING CONFIGURATION: {}".format(e)
            )
            return

        _log.info("[G36 Agent INFO] - ALL Subscribition Success!!")

    def _create_subscriptions(self, topics):
        """
        Unsubscribe from all pub/sub topics and create a subscription to a topic in the configuration which triggers
        the _handle_publish callback
        """
        self.vip.pubsub.unsubscribe("pubsub", None, None)

        _log.info(f"[G36 Agent INFO] -  _create_subscriptions {topics}")
        self.vip.pubsub.subscribe(
            peer="pubsub", prefix=topics, callback=self._handle_publish
        )

    def _handle_publish(self, peer, sender, bus, topic, headers, message):
        """
        When we recieve an update from our all publish subscription, log something so we can see that we are
        successfully scraping CSV points with the Platform Driver
        :param peer: unused
        :param sender: unused
        :param bus: unused
        :param topic: unused
        :param headers: unused
        :param message: "All" messaged published by the Platform Driver for the CSV Driver containing values for all
        registers on the device
        """
        for ahu in self.ahus_as_a_class:
            topic = topic.strip("/all")
            _log.info(f"*** [G36 Agent INFO] *** {ahu} {topic}")
            _log.info(f"*** [G36 Agent INFO] *** {ahu} {message[0]}")

            # append value for the duct pressure setpoint
            duct_static_setpoint_ = message[0].get(getattr(ahu, "duct_static_setpoint"))
            _log.info(
                f"[G36 Agent INFO] - Duct Static Pressure Setpoint is: {duct_static_setpoint_}"
            )
            getattr(ahu, "duct_static_setpoint_data").append(duct_static_setpoint_)

            # append value for the duct pressure
            duct_static_ = message[0].get(getattr(ahu, "duct_static"))
            _log.info(f"[G36 Agent INFO] - Duct Static Pressure is: {duct_static_}")
            getattr(ahu, "duct_static_data").append(duct_static_)

            # append value for the vfd speed
            vfd_speed_ = message[0].get(getattr(ahu, "vfd_speed"))
            _log.info(f"[G36 Agent INFO] - AHU Fan VFD Speed is: {vfd_speed_}")
            getattr(ahu, "vfd_speed_data").append(vfd_speed_)

            # append value for the outdoor temp
            outdoor_air_temp_ = message[0].get(getattr(ahu, "outdoor_air_temp"))
            _log.info(f"[G36 Agent INFO] - Outside Air Temp is: {outdoor_air_temp_}")
            getattr(ahu, "outdoor_air_temp_data").append(outdoor_air_temp_)

            # append value for the return air temp
            return_air_temp_ = message[0].get(getattr(ahu, "return_air_temp"))
            _log.info(f"[G36 Agent INFO] - Return Air Temp is: {return_air_temp_}")
            getattr(ahu, "return_air_temp_data").append(return_air_temp_)

            # append value for the supply air temp
            mixing_air_temp_ = message[0].get(getattr(ahu, "mixing_air_temp"))
            _log.info(f"[G36 Agent INFO] - Supply Air Temp is: {mixing_air_temp_}")
            getattr(ahu, "mixing_air_temp_data").append(mixing_air_temp_)

            # pass this class to see if enough data to calc rolling avg
            """
            TODO implement if else for each fc equation and a pass if its
            not inside the config OMIT
            """
            
            self.fault_checker_fc1(ahu)
            self.fault_checker_fc2(ahu)
            
            # future all the way up to fc 13
            # self.fault_checker_fc3(ahu)
            # self.fault_checker_fc4(ahu)
            # self.fault_checker_fc5(ahu)
            # self.fault_checker_fc6(ahu)
            # self.fault_checker_fc7(ahu)

    def fault_checker_fc1(self, ahu):
        len_of_list_fc1 = len(getattr(ahu, "duct_static_setpoint_data"))

        _log.info(
            f"[G36 Agent INFO] - fc1 on {ahu} list len check is {len_of_list_fc1}"
        )

        if len_of_list_fc1 < 5:
            _log.info(
                f"[G36 Agent INFO] - Not enough accumilated data to run fc1 fault checker"
            )
            return

        else:
            data = {
                "duct_static_setpoint": getattr(ahu, "duct_static_setpoint_data"),
                "duct_static": getattr(ahu, "duct_static_data"),
                "supply_vfd_speed": getattr(ahu, "vfd_speed_data"),
            }

            df = pd.DataFrame(data)

            _log.info(f"[G36 Agent INFO] - NOT rolling fc1 df is {df}")

            df = df.rolling(window=5).mean().dropna()
            _log.info(f"[G36 Agent INFO] - rolling fc1 df is {df}")

            _fc1 = FaultConditionOne(
                self.vfd_speed_percent_err_thres,
                self.duct_static_inches_err_thres,
                self.vfd_speed_percent_max,
                "duct_static",
                "supply_vfd_speed",
                "duct_static_setpoint",
            )

            df2 = _fc1.apply(df)

            # Pandas df access the fault element in the last row
            # Int of one is Fault and zero for no fault
            fc1_fault = df2.at[df2.index[-1], "fc1_flag"]

            _log.info(f"[G36 Agent INFO] - fault_checker_fc1 is {fc1_fault}")

            getattr(ahu, "duct_static_setpoint_data").clear()
            getattr(ahu, "duct_static_data").clear()
            
            #getattr(ahu, "vfd_speed_data").clear()

            """
            #publish to message bus
            self.vip.pubsub.publish(
                peer="pubsub",
                topic=f"analysis",
                headers={
                    headers.TIMESTAMP: utils.format_timestamp(utils.get_aware_utc_now())
                },
                message=f"FAULTS_FC1/{self.ahu_instance_id}/{int(fdd_check)}",
            )
            """

    def fault_checker_fc2(self, ahu):

        len_of_list_fc2 = len(getattr(ahu, "mixing_air_temp_data"))

        _log.info(
            f"[G36 Agent INFO] - fc2 on {ahu} list len check is {len_of_list_fc2}"
        )

        if len_of_list_fc2 < 5:
            _log.info(
                f"[G36 Agent INFO] - Not enough accumilated data to run fc2 fault checker"
            )
            return

        else:
            data = {
                "outdoor_air_temp": getattr(ahu, "outdoor_air_temp_data"),
                "return_air_temp": getattr(ahu, "return_air_temp_data"),
                "mixing_air_temp": getattr(ahu, "mixing_air_temp_data"),
                "supply_vfd_speed": getattr(ahu, "vfd_speed_data"),
            }

            df = pd.DataFrame(data)

            _log.info(f"[G36 Agent INFO] - NOT rolling fc2 df is {df}")

            df = df.rolling(window=5).mean().dropna()
            _log.info(f"[G36 Agent INFO] - rolling fc2 df is {df}")

            _fc2 = FaultConditionTwo(
                self.mix_degf_err_thres,
                self.return_degf_err_thres,
                self.outdoor_degf_err_thres,
                "mat",
                "rat",
                "oat",
                "supply_vfd_speed",
            )

            df2 = _fc2.apply(df)

            # Pandas df access the fault element in the last row
            # Int of one is Fault and zero for no fault
            fc2_fault = df2.at[df2.index[-1], "fc2_flag"]

            _log.info(f"[G36 Agent INFO] - fault_checker_fc2 is {fc2_fault}")

            getattr(ahu, "outdoor_air_temp_data").clear()
            getattr(ahu, "return_air_temp_data").clear()
            getattr(ahu, "mixing_air_temp_data").clear()
            getattr(ahu, "vfd_speed_data").clear()

            """
            #publish to message bus
            self.vip.pubsub.publish(
                peer="pubsub",
                topic=f"analysis",
                headers={
                    headers.TIMESTAMP: utils.format_timestamp(utils.get_aware_utc_now())
                },
                message=f"FAULTS_FC1/{self.ahu_instance_id}/{int(fdd_check)}",
            )
            """

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.

        Usually not needed if using the configuration store.
        """
        pass

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """
        pass

    @RPC.export
    def rpc_method(self, arg1, arg2, kwarg1=None, kwarg2=None):
        """
        RPC method

        May be called from another agent via self.core.rpc.call
        """
        return self.setting1 + arg1 - arg2


def main():
    """Main method called to start the agent."""
    utils.vip_main(faultmachine, version=__version__)


if __name__ == "__main__":
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
