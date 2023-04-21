from bacpypes.object import BinaryValueObject, register_object_type
from bacpypes.local.object import AnalogValueCmdObject
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import BinaryValueObject, register_object_type
from bacpypes.local.device import LocalDeviceObject
from bacpypes.local.object import AnalogValueCmdObject
from bacpypes.consolelogging import ConfigArgumentParser


# Register object type
register_object_type(AnalogValueCmdObject, vendor_id=999)

class BacnetApp:
    def __init__(self):
        self.supply_air_static_pressure_av = 0
        self.supply_air_static_pressure_setpoint_av = 0
        self.fan_vfd_av = 0
        self.fan_vfd_err_thres_pv = 0
        self.fan_vfd_max_speed_err_thres_pv = 0
        self.supply_air_static_pressure_err_thres_pv = 0
        self.bacnet_app = None
        self.point_classes = {
            "analogValue": {
                "class": AnalogValueCmdObject,
                "params": {
                    "presentValue": 0.0,
                    "statusFlags": [0, 0, 0, 0],
                    "covIncrement": 1.0,
                },
            },
            "binaryValue": {
                "class": BinaryValueObject,
                "params": {
                    "presentValue": "inactive",
                    "statusFlags": [0, 0, 0, 0],
                },
            },
        }

    def make_points(self, point_tuples):
        points = []
        for i, (point_id, point_name) in enumerate(point_tuples):
            if point_id not in self.point_classes:
                raise ValueError(f"Unsupported point type: {point_id}")

            point_class = self.point_classes[point_id]["class"]
            point_params = self.point_classes[point_id]["params"]

            point = point_class(
                objectIdentifier=(point_id, i+1),
                objectName=point_name,
                **point_params,
            )

            points.append(point)

        return points
    
    
    def make_app(self,brick_tuple):
        
        parser = ConfigArgumentParser(description=__doc__)
        args = parser.parse_args()
        this_device = LocalDeviceObject(ini=args.ini)
        fault_detector_application = BIPSimpleApplication(this_device, args.ini.address)

        points = self.make_points(brick_tuple)

        point_vars = {}
        for point_id, point_name in brick_tuple:
            for point in points:
                if point.objectIdentifier[0] == point_id and point.objectName == point_name:
                    point_vars[point_name] = point

        self.fan_vfd_err_thres_av = point_vars["fan_vfd_err_thres"]
        fault_detector_application.add_object(self.fan_vfd_err_thres_av)
        
        self.fan_vfd_max_speed_err_thres_av = point_vars["fan_vfd_max_speed_err_thres"]
        fault_detector_application.add_object(self.fan_vfd_max_speed_err_thres_av)
        
        self.supply_air_static_pressure_err_thres_av = point_vars[
            "supply_air_static_pressure_err_thres"
        ]
        fault_detector_application.add_object(self.supply_air_static_pressure_err_thres_av)
        
        self.supply_air_static_pressure_av = point_vars["supply_air_static_pressure"]
        fault_detector_application.add_object(self.supply_air_static_pressure_av)
        
        self.supply_air_static_pressure_setpoint_av = point_vars[
            "supply_air_static_pressure_setpoint"
        ]
        fault_detector_application.add_object(self.supply_air_static_pressure_setpoint_av)
        
        self.fan_vfd_av = point_vars["fan_vfd"]
        fault_detector_application.add_object(self.fan_vfd_av)
        
        self.fault_condition_one_alarm_bv = point_vars["fault_condition_one_alarm"]
        fault_detector_application.add_object(self.fault_condition_one_alarm_bv)
        
        self.bacnet_app = this_device