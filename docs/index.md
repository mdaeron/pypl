---
hide:
  - toc
---

# Python Prep Line (PyPL)

An open source, open hardware, automated preparation line for processing geochemical samples. Originally designed for CO<sub>2</sub> samples, but should handle anything which requires:

* switching relays, valves or heating elements
* monitoring temperature sensors (e.g., [thermocouples](https://en.wikipedia.org/wiki/Thermocouple) or [RTD](https://en.wikipedia.org/wiki/Resistance_thermometer) sensors)
* monitoring MKS vacuum/pressure gauges.
* controlling [stepper motors](https://en.wikipedia.org/wiki/Stepper_motor)

The user interface runs on a raspberry pi computer but this computer may be switched off or unplugged without affecting automated processes, which remain running on an independent microcontroller which handles lower-level interaction with sensors and various electronic components.

Modifying hardware configuration and sample preparation protocols is easily done using [Python](https://www.python.org) (on the computer) and [MicroPython](https://micropython.org) (on the microcontroller).

## Contributors

Originally created by [Mathieu Daëron](https://daeron.fr), with advice, contributions and feedback from Samir Kassi, Arnaud Dapoigny, and Justin Chaillot.
