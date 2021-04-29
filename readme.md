<img src="css.svg" alt="">

<h1>HELLO WORLD!</h1>

# Python Prep Line (PyPL)

An open source, open hardware, automated preparation line for geochemical samples. Originally designed for processing CO<sub>2</sub> samples, but should handle anything which requires:

* switching relays, valves or heating elements
* monitoring temperature sensors (e.g., PT1000 sensors; type-K thermocouples)
* monitoring MKS vacuum/pressure gauges.
* controlling stepper motors

## Hardware
### Motherboard
### Pyboard
### Stepper Motor Controller Board
### Temperature Readings

Up to 4 independent temperature reading. Each reading may come from either:

* a thermocouple connected to a MAX31856 chip
* a resistance temperature detector (PT1000 or PT100) connected to a MAX31865 chip

#### Thermocouple Board

* [Adafruit 3263](https://www.adafruit.com/product/3263)
* Based on MAX31856

![adafruit_3263](pictures/adafruit_3263.png)

#### PT1000 Board

* [Adafruit 3328](https://www.adafruit.com/product/3328)
* Based on MAX31865

![adafruit_3328](pictures/adafruit_3328.png)

### Thermocouples (type K)

* Supplier: https://www.prosensor.fr
* Part #: K4051000-2-1/TEF
* OD = 0.5 mm
* L = 1 m

### Heating Elements
* Supplier: https://www.prosensor.fr
* Part #: CCHC-1/4-11/4-300-0 or CCHC-6.5-30-300-0
* 300 W at 230 VAC
* OD = 6.35 mm or 6.5 mm
* L = 31.75 mm or 30 mm

![heating_element](pictures/heating_element.png)

### Pressure Readings

#### MicroPirani and DualTrans Vacuum/Pressure Gauges

* Part #: [MKS 925](https://www.mksinst.com/f/925-micro-pirani-vacuum-transducer)
* Part #: [MKS 910](https://www.mksinst.com/f/910-micro-pirani-vacuum-transducer)
* Communicates through an RS232 serial connection

![mks_910](pictures/mks_910.png)

#### RS232 / TTL Transceiver Board

Converts TTL (Transistor-Transistor Logic) signals to and from RS232 signals

* [SparkFun Transceiver Breakout (BOB-11189)](https://www.sparkfun.com/products/11189)
* Based on MAX3232

![sparkfun_11189](pictures/sparkfun_11189.png)

### Relays

The pyboard communicates through I2C with a GPIO expansion board based on the MCP23017 chip, providing access to 16 input or output ports. Each of these ports is connected to a power MOSFET, providing the ability to quickly switch DC power to 16 screw terminals.

#### GPIO Expansion Board

* Based on MCP23017
* All ports are pulled low (connected to ground by 10K resistors).
* As a result, all switches are off by default.

![mcp23017](pictures/mcp23017.png)

#### Power MOSFETSs

Used to connect screw terminals to ground safely and quickly. This means that when the MOSFET is off, whatever is connected to the screw terminals will float at a moderately high DC voltage (e.g., 24 VDC) despite being powered off, so any electrical connections should be suitably insulated.

![mosfet](pictures/mosfet.png)


### Power Supply
### Aluminum Frame
### Acid Reaction System
#### Common Acid Bath
#### Sample Carousel
### Pumping System
## Software
### Pyboard Code
### GUI Code

<img src="css.svg" alt="">
