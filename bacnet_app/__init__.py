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
        self.bacnet_app = None
        self.point_classes = {
            "analogValue": {
                "class": AnalogValueCmdObject,
                "params": {
                    "statusFlags": [0, 0, 0, 0],
                    "covIncrement": 1.0,
                },
            },
            "binaryValue": {
                "class": BinaryValueObject,
                "params": {
                    "statusFlags": [0, 0, 0, 0],
                },
            },
        }
        self.points = {}

    def make_points(self, point_tuples):
        points = []
        for i, (point_id, point_name, default_value, description) in enumerate(
            point_tuples
        ):
            if point_id not in self.point_classes:
                raise ValueError(f"Unsupported point type: {point_id}")

            point_class = self.point_classes[point_id]["class"]
            point_params = self.point_classes[point_id]["params"]

            point = point_class(
                objectIdentifier=(point_id, i + 1),
                objectName=point_name,
                presentValue=default_value,
                description=description,
                **point_params,
            )

            points.append(point)
            self.points[point_name] = point

        # assign variables
        for point_name in self.points:
            if "alarm" not in point_name:
                var_name = point_name.replace("-", "_") + "_av"
                setattr(self, var_name, self.points[point_name])
            else:
                var_name = point_name.replace("-", "_") + "_bv"
                setattr(self, var_name, self.points[point_name])

        return points

    def make_app(self, brick_tuple):
        parser = ConfigArgumentParser(description=__doc__)
        args = parser.parse_args()
        this_device = LocalDeviceObject(ini=args.ini)
        fault_detector_application = BIPSimpleApplication(this_device, args.ini.address)
        points = self.make_points(brick_tuple)
        for point in points:
            fault_detector_application.add_object(point)

        self.bacnet_app = this_device
