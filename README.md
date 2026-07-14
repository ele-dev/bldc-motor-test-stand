# Custom BLDC Motor & Propeller Thrust Stand

An automated, hardware-in-the-loop (HIL) testing platform designed to characterize brushless DC (BLDC) motor and propeller combinations. This system replaces unpredictable battery testing with a programmable power supply to deliver highly repeatable, scientific propulsion data while programmatically simulating real-world battery behavior.

---

## Project Goal

The primary objective of this project is to build a unified desktop application that automates propulsion testing. By executing controlled, stepwise throttle sweeps, the system captures stationary physical and electrical metrics to generate precise, empirical performance curves (such as thrust vs. RPM, power vs. RPM, and overall system efficiency).

### Key Features

* **Automated Stepwise Testing:** Ramps the motor throttle sequentially (e.g., 0% to 100% in 5% increments) and pauses at each step to allow aerodynamic slipstreams to fully settle before sampling.
* **Software-Defined Battery Emulation:** Eliminates the variables of physical LiPo batteries (state of charge drift, temperature, internal resistance degradation) while retaining real-world fidelity. The software calculates dynamic voltage sag ($V_{term} = V_{ocv} - I \cdot R_{int}$) in real time to simulate realistic in-flight voltage drops.
* **Synchronized Telemetry Logging:** Merges 24-bit physical force readings from a load cell and high-frequency RPM metrics with precise voltage, current, and power data queried via SCPI from a programmable power supply.
* **Instant Curve Fitting & Visualization:** Automatically fits 2nd-degree (quadratic) and 3rd-degree (cubic) polynomials to the aggregated datasets to map thrust and power curves natively within the application.

---

## System Architecture

The system is split into three core layers to isolate low-latency hardware tasks from high-level data orchestration:
1.  **High-Level Controller (Python):** Manages the test state machine, performs the battery emulation math, queries the bench power supply, and logs all data.
2.  **Low-Level Controller (Arduino Nano):** Generates a hardware-timed, rock-solid **200 Hz PWM signal** to drive the ESC and reads the **HX711 load cell amplifier** (hardware-modded to 80 Hz) to capture high-resolution force data without latency spikes.
3.  **Programmable DC Source (OWON SPE8205):** Acts as the high-current, regulated power backbone and delivers real-time voltage and current telemetry via SCPI.
