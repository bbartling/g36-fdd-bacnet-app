## Fault Detection BACnet Server App

### Concept idea for HVAC fault detection in real time on the edge or Operations Technology (OT) Local Area Network (LAN) inside the building:
![Alt text](/images/schematic.jpg)

### See subfolders for algorithm concept implementations based on these definitions:
* [AHU](https://github.com/bbartling/open-fdd/tree/master/air_handling_unit/images)
* Boiler Plant - still to come
* Chiller Plant - still to come

### Install bacpypes:
`$ pip install bacpypes`

* Modify the `bacpypes.ini` for your devices IP address

### Tested on Ubuntu LTS 22.04 Python 3.10, run app:
`$ python main.py`







