## Fault Detection BACnet Server App

### future concept idea for a BACnet device that BAS contractors can deploy that will collect HVAC IO data via supervisory level logic and 
then represent faults as BACnet objects that can be trended/alarmed on the BAS.

### See subfolders for algorithm concept implementations based on these definitions:
* [AHU](https://github.com/bbartling/open-fdd/tree/master/air_handling_unit/images)
* Boiler Plant - still to come
* Chiller Plant - still to come

### Install bacpypes:
`$ pip install bacpypes`

* Modify the `bacpypes.ini` for your devices IP address

### Tested on Ubuntu LTS 22.04 Python 3.10, run app:
`$ python main.py`







