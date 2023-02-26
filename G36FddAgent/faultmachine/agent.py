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

from faultmachine import FaultConditionOne

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


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
        
        self.duct_static_setpoint_data = []
        self.duct_static_data = []
        self.vfd_speed_data = []

        # G36 default FC1 params for the FDD algorithm
        self.vfd_speed_percent_err_thres = 0.05
        self.duct_static_inches_err_thres = 0.99
        self.vfd_speed_percent_max = 0.1

    def configure(self, config_name, action, contents):
        """
        Called after the Agent has connected to the message bus. If a configuration exists at startup
        this will be called before onstart.

        Is called every time the configuration in the store changes.
        """
        config = self.default_config.copy()
        config.update(contents)

        _log.info("[G36 Agent INFO] - Configuring Agent")

        try:
            _log.info(f"[G36 Agent INFO] - {config}")
            
            for fault in config:
                _log.info(f"[G36 Agent INFO] - {fault}")
                        
                ahu_instance_id = str(config["ahu_instance_id"])
                building_topic = str(config["building_topic"])
                duct_static_setpoint = str(config["duct_static_setpoint"])
                duct_static = str(config["duct_static"])
                vfd_speed = str(config["vfd_speed"])

        except ValueError as e:
            _log.error(
                "[G36 Agent INFO] - ERROR PROCESSING CONFIGURATION: {}".format(e)
            )
            return

        self.ahu_instance_id = ahu_instance_id
        self.building_topic = building_topic
        self.duct_static_setpoint = duct_static_setpoint
        self.duct_static = duct_static
        self.vfd_speed = vfd_speed

        _log.info("[G36 Agent INFO] - Configs Set Success")
        
        subscription_prefix = f"devices/{self.building_topic}/{self.ahu_instance_id}/"
        _log.info(f"[G36 Agent INFO] - subscribe to: {subscription_prefix}")

        self.vip.pubsub.subscribe(
            peer="pubsub",
            prefix=subscription_prefix,
            callback=self._handle_publish,
        )
        
        _log.info("[G36 Agent INFO] - Subscribe Success!!")

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
        
        topic = topic.strip("/all")
        _log.info(f"*** [G36 Agent INFO] *** topic_formatted {topic}")
        _log.info(f"*** [G36 Agent INFO] *** message[0] is {message[0]}")

        # append value for the duct pressure setpoint
        duct_static_setpoint_ = message[0].get(self.duct_static_setpoint)
        _log.info(
            f"[G36 Agent INFO] - Duct Static Pressure Setpoint is: {duct_static_setpoint_}"
        )
        self.duct_static_setpoint_data.append(duct_static_setpoint_)

        # append value for the duct pressure
        duct_static_ = message[0].get(self.duct_static)
        _log.info(f"[G36 Agent INFO] - Duct Static Pressure is: {duct_static_}")
        self.duct_static_data.append(duct_static_)

        # append value for the vfd speed
        vfd_speed_ = message[0].get(self.vfd_speed)
        _log.info(f"[G36 Agent INFO] - AHU Fan VFD Speed is: {vfd_speed_}")
        self.vfd_speed_data.append(vfd_speed_)

        self.fault_checker()
        
        
    def fault_checker(self):
        _log.info(f"[G36 Agent INFO] - fault_checker GO!: \
            {len(self.duct_static_setpoint_data)}")

        if len(self.duct_static_setpoint_data) < 5:
            _log.info(
                f"[G36 Agent INFO] - Not enough accumilated data to run fault checker")
            return

        else:

            data = {
                "duct_static": self.duct_static_data, 
                "duct_static_setpoint": self.duct_static_setpoint_data, 
                "supply_vfd_speed": self.vfd_speed_data
            }
            
            df = pd.DataFrame(data)
            
            _log.info(f"[G36 Agent INFO] - NOT rolling df is {df}")

            df = df.rolling(window=5).mean().dropna()
            _log.info(f"[G36 Agent INFO] - rolling df is {df}")
            
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
            fc1_fault = df2.at[df2.index[-1], 'fc1_flag']
            
            _log.info(f"[G36 Agent INFO] - fault_condition_one is {fc1_fault}")

            self.duct_static_setpoint_data.clear()
            self.duct_static_data.clear()
            self.vfd_speed_data.clear()

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
