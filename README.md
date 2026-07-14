# Automated BLDC Motor & Propeller Thrust Stand

An automated, hardware-in-the-loop (HIL) testing platform designed to systematically characterize brushless DC (BLDC) motor and propeller combinations. By orchestrating a programmable DC power supply, a dedicated microcontroller, and a physical load sensor, this system replaces manual, error-prone testing with a unified, software-driven workflow.

---

## What is it?
This is an integrated hardware-and-software test bench that automates the collection of aerodynamic and electrical performance metrics. The setup pairs a Python control application with an Arduino Nano (for low-level actuator control and force sensing) and an OWON SPE8205 programmable bench power supply (acting as the regulated, metered power source).

## What is it for?
The platform is built to evaluate the efficiency, thrust output, and power consumption of various motor and propeller pairings. It is used to:
* **Generate empirical performance curves** (e.g., Thrust vs. RPM, Power vs. RPM, and overall Grams-per-Watt efficiency).
* **Compare different hardware configurations** under identical, highly repeatable test conditions.
* **Collect clean engineering data** to inform aircraft design, flight endurance estimates, and propulsion matching.

## What is the core idea?
The core idea is to perform standardized, automatic motor-propeller tests and capturing sensor data in the process 
to gain insights and visualizations.