# volttron-g36-fdd
[VOLTTRON](https://github.com/VOLTTRON/volttron) edge device agent for HVAC systems Fault Detection Diagnostics as defined by ASHRAE Guideline 36. 
This agent will listen to the VOLTTRON message bus on the edge device and capture data for HVAC systems operations and perform fault detection based on ASHRAE G36 equations.


To run on the edge device in the VOLTTRON framework with the platform bootstrapped properly, the virtual enviornment up and running, 
and after the VOLTTRON BACnet proxy is properly scraping data on 1 minute intervals:

```shell
$ pip install pandas

$ vctl config store platform.fddagent config ./G36FddAgent/config

$ python scripts/install-agent.py -s ./G36FddAgent -c ./G36FddAgent/config  --tag fdd_agent -i platform.fddagent -f

$ vctl start --tag fdd_agent
```

G36 requires data to be scraped on 1 minute intervals and for data to be in a 5 minute rolling average format. 
This agent requires that the BACnet system is being scraped on one minute intervals where then internally 
Python code in this agent uses the Pandas library that will accomodate the rolling average computations and then publish 
a fault to the VOLTTRON message bus as a int `1` or a `0` for normal conditions. Fault equations in this agents `__init__.py` 
maybe updated periodically based on a seperate git repository [open-fdd](https://github.com/bbartling/open-fdd) for the study and reporting of the G36 FDD on historical datasets.

## Author

[linkedin](https://www.linkedin.com/in/ben-bartling-510a0961/)

## Licence

【MIT License】

Copyright 2022 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
