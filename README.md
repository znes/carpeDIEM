# carpeDIEM

The repository provides scripts to build carpeDIEM (http://project-carpediem.eu/) energy datapackages in directory datapackages/ and to solve the defined systems towards least-cost optimality. carpeDIEM itself contains only two short scripts, build.py and compute.py, because it relies on the Open Energy Modeling Framework - oemof. These datapackages are based on a reference input dataset developed at https://github.com/ZNES-datapackages/Status-quo-2015.

## Archived input data / data.xls

Data on the preoptimized sub-system is contained in a separate xls file.

```
--| scenarios

Contains a short-list of scenario labels and names.

--| timeseries-2A --| timeseries-2B ...

Timeseries data especially for the isolated approach with an effect to the German electricity hub.
On the one hand pre-optimized residual load timeseries of the sub-system and on the other hand
demand or generation no longer associated with the macro-system. The net-balance is connected to
the German eletricity bus.

--| r_residuals --| r_profiles

Preoptimized timeseries of the sub-system. Wind, pv and load profile of the sub-system.

--| r_aux

In essence auxiliary values, with which the profiles of the sub-system get multiplied.
```

## Installation

Please install the required dependencies.

	pip install six

	pip install --no-deps -r requirements.txt

## Installation from scratch

In order to run the scripts written in Python on a clean install of Ubuntu Linux (Tested on Ubuntu 18.04.2 LTS) follow these steps.

Open up a terminal (Ctrl + Alt + T), a command-line interface to interact with the operating system.

Install the package-installer for Python (pip) maintained by the Python Packaging Authority. With pip you can install additional Python packages from the Python Package Index (pypi).

	sudo apt-get install python3-pip

Install the open source mixed integer programming solver Cbc (Coin-or branch and cut), used to solve the mathematical model representation of the electricity system.

	sudo apt-get install coinor-cbc

Clone the carpeDIEM git repository and change your working directory.

	git clone https://github.com/znes/carpeDIEM.git

	cd carpeDIEM

Install required Python packages with pip.

	pip3 install six

	pip3 install --no-deps -r requirements.txt

Run the build-script, which creates a datapackage for each carpeDIEM-scenario.

	python3 build.py

Afterwards run the compute-script to optimize these energy system configurations.

	python3 compute.py

Change your directory to view the results.

	cd ~/results


## Project

An electricity sub-system / micro-system, e.g. a municipality, is analysed in the context of a so-called macro-system, e.g. a national state. The sub-system, Bordelum, is pre-optimized independently from the macro-system with a focus on varying degrees of autarky. As such it is a showcase for the effects of autarkic sub-systems in a minimal cost optimized German electricity system.
