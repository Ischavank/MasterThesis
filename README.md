# Autonomous Greenhouse Robot for Plant Monitoring and Irrigation Support

This repository contains the sofware developed for the Master Thesis project focused on an autonomous robot operating inside a greenhouse environment
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


