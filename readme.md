# Python Prep Line (PyPL)

An open source / open hardware automation system. Originally designed for processing geochemichal samples in our stable isotope lab, but the system is flexible enough to fit many other needs.

## Core design

* Microcontrollers are not encumbered by a full OS, yet can reliably run simple tasks with low latency (μs to ms).
* PyPL uses a *pyboard*, a microcontroller running MicroPython (a full-featured Python implementation running on “bare metal”) to communicate asynchronously with sensors
(T, P, H), and actuators (stepper motors, relays, valves, heating elements...).
* The board is also connected to a full-fledged computer (e.g., a Raspberry Pi or something more expensive) which provides a GUI and logs/syncs/backups data.
* PyPL mostly uses cheap (2–20 €) breakout boards for electronic components, making most repairs plug-and-play. These boards are cheap enough that you can have spare ones, further simplifying hardware maintenance.
* All code, whether on the pyboard or on the computer, is regular Python, promoting painless
development, rapid iteration, and future-proof code.

## Documentation

Full documentation (work in progress) is [here](https://mdaeron.github.io/pypl/).
