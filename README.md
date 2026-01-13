# Autonomous Greenhouse Robot for Plant Monitoring and Irrigation Support

This repository contains the sofware developed for the Master Thesis project focused on an autonomous robot operating inside a greenhouse environment.

The robot follows a physical tape line using computer vision, detects plants using QR code recognition, collect environmental specific data and plant health data using sensors and a plant API health assessment, and provides irrigation decision making.

The system is designed to run on a Raspberry Pi and integrates cameras, sensors, APIs, and machine learning models into a single platform.

---

## System Overview

The robot performs the following tasks:

 - Line following for navigation using a downward facing camera
 - Plant detection using a forward facing camera and QR code detection (plant detection available using YOLO model, but computational too heavy)
 - Environmental sensing (temperature, humidity, soil moisture)
 - Data logging
 - External data integration via weather and plant APIs
 - Support for multiple operating modes (data gathering, testing, autonomous opertion)

---

## Hardware Components

- Raspberry Pi 5
- Raspberry Pi camera module 3 (2x)
  - Downward facing for tape following
  - Side facing for plant detection and plant photo API
- BME280 environmental sensor (temperature & humidity)
- Soil moisture sensor
- Mobile robot platform

---

## Repository Structure

The repository is organised by subsystem and by execution mode:

**Entry points (run modes)**
- `main.py` — autonomous run (full system)
- `mainDataGathering.py` — data collection mode
- `mainRobotTesting.py` — robot testing mode
- `mainSystemTesting.py` — system integration testing mode

**Perception (vision)**
- `robot_vision.py` — tape line following
- `qr_vision_Real.py` — QR detection for real operation
- `qr_vision_RobotTesting.py` — QR detection during robot testing
- `robot_vision_SystemTesting.py` — vision code used in system tests

**Sensors & logging**
- `sensorBM280.py` — BME280 interface
- `soil_moist.py` — soil moisture sensor interface
- `data_logger.py` — logging utilities

**Models**
- `model_usage.py` — model loading/inference
- `confidence.py` — confidence handling / thresholds
- `model/` — model-related outputs/artifacts

**APIs**
- `plant_api.py` — plant health/plant database interface
- `weather_api.py` — weather data interface

**Data and experiments**
- `data/` — logged data (may be excluded from Git depending on size)
- `testing/` — scripts and experiments used during development/testing

---

**Machine Learning Models and Data Workflow**

Soil moisture data is collected separately during robot operation and logged together with environmental and plant-related information.
This data is not used for real-time control but serves as input for offline machine learning models.

The trained models are stored in the following directories:

`data/model/BasicModel`

`data/model/IntermediateModel`

`data/model/FinalModel`

These models are trained after data collection and are used to generate irrigation advice based on historical sensor data, plant health indicators, and environmental conditions.
The separation between data collection and model inference reflects the experimental nature of the project and allows different model versions to be evaluated without modifying the robot control software.

---

## Running the System

Note: The code is designed for Raspberry Pi hardware (cameras + sensors). Some scripts require connected hardware to run.

Autonomous operation (full system)
- `python3 main.py`

Data gathering mode
- `python3 mainDataGathering.py`

Robot testing mode
- `python3 mainRobotTesting.py`

System testing mode
- `python3 mainSystemTesting.py`

---

## Thesis


This repository accompanies a Master Thesis project on an autonomous greenhouse robot for plant monitoring and irrigation decision support
