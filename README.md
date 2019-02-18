# carpeDIEM

Builds showcase datapackages in the context of the carpeDIEM project by downloading and updating the ZNES Status-quo datapackage.

## Installation

Please install the required dependencies.

`pip install -r requirements.txt`


## Installation from scratch

In order to run the scripts written in Python on a clean install of Ubuntu Linux (Tested on Ubuntu 18.04.2 LTS) follow these steps.

Open up a terminal (Ctrl + Alt + T), a command-line interface to interact with the operating system.

Install the package-installer for Python (pip) maintained by the Python Packaging Authority. With pip you can install additional Python packages from the Python Package Index (pypi).

`sudo apt-get install python3-pip

Install the open source mixed integer programming solver Cbc (Coin-or branch and cut), used to solve the mathematical model representation of the electricity system.

`sudo apt-get install coinor-cbc`

Clone the carpeDIEM git repository and change your working directory.

`git clone https://github.com/znes/carpeDIEM.git`

`cd carpeDIEM`

Install required Python packages with pip.

`pip3 install -r requirements.txt`

Run the build-script, which creates a datapackage for each carpeDIEM-scenario.

`python3 build.py`

Afterwards run the compute-script to optimize these energy system configurations.

`python3 compute.py`

Change your directory to view the results.

`cd ~/results`


## Project

An electricity sub-system / micro-system, e.g. a municipality, is analysed in the context of a so-called macro-system, e.g. a national state. The sub-system, Bordelum, is pre-optimized independently from the macro-system with a focus on varying degrees of autarky. As such it is a showcase for the effects of autarkic sub-systems in a minimal cost optimized German electricity system.

## Showase system settings

In order to reach varying degrees of autarky in Bordelum different system settings are assumed.

| Name                                | System setting | Demand | PV   | Wind power | CHP      | Batteries | Batteries    | Batteries    | Batteries             |
|-------------------------------------|----------------|--------|------|------------|----------|-----------|--------------|--------------|-----------------------|
| ---                                 |     ---        | ---    |---   | ---        | ---      | Capacity  | Charging     | Discharging  | Efficiency (one way)  |
|  ---                                |                | MWh/a  |kwp   | kW         | kWel     | kWh       | kW (in)      | kW (out)     | per unit              |
| Base case                           | A              | 985.681| 2940 |            |          |           |              |              |                       |
| Prosumer batteries                  | B              | 985.681| 2940 |            |          | 349.2     | 180          | 165.6        | 95.00                 |
| Prosumer expansion                  | C              | 985.681| 4269 |            |          | 1678.1    | 865          | 795.8        | 95.00                 |
| Centralized battery                 | D              | 985.681| 2940 |            |          | 2263      | 1000         | 1000         | 85.00                 |
| Wind-turbine                        | E              | 985.681| 2940 | 1000       |          |           |              |              |                       |
| Wind-turbine and centralized battery| F              | 985.681| 2940 | 1000       |          | 560       | 560          | 1000         | 92.00                 |
| Combined heat and power             | G              | 1735.681|2940 |            | 875      |           |              |              |                       |

Hoeck2018, NEPGH2012
