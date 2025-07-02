# Steering-Aware LIDAR Visualization Dashboard
This project displays real-time LIDAR data and the vehicle’s steering angle to support navigation. It features a live table, a radar chart of the surroundings, and a car model that turns with the steering. This helps visualize the car’s path and nearby objects, useful in robotics and autonomous vehicles.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Objective of the Work](#objective-of-the-work)
- [GUI Preview](#gui-preview)
- [How to Test](#how-to-test)
- [Future Scope](#future-scope)

## Introduction
This project presents a real-time dashboard designed to visualize LIDAR sensor data alongside a vehicle’s steering angle. The system captures live TCP stream data from a LIDAR sensor and renders it into a responsive and interactive GUI.

Key elements of the dashboard include:
* A radar-style chart that visually represents the surrounding objects.

* A live-updating data table showing detailed angle, distance, and intensity values.

* A car model that turns to reflect real-time steering angle using Ackermann geometry.

This tool is highly useful for applications in autonomous vehicles, robotics, and mobile navigation systems, where understanding environmental layout and steering dynamics is crucial.


## Features
* Real-time data from a LIDAR sensor (TCP stream).
* Live updating data table and radar scanner view.
* Visual steering indicator based on angle.
* Flask backend + HTML/CSS/JS frontend.
* Responsive and interactive GUI layout.

## Tech Stack
* Backend: Python, Flask
* Frontend: HTML, CSS, JavaScript
* Data Source: LIDAR Sensor
* Charting: Custom Radar Chart

## Objective of the Work
The main goal of this project is to develop a real-time visualization dashboard for a Robotic Mobile Vehicle (RMV) that:

* Displays live LIDAR scan data to detect surrounding obstacles.

* Computes and shows the vehicle’s steering angle using Ackermann steering geometry.

* Helps in trajectory planning and navigation of the vehicle for tasks such as automated painting or movement in constrained environments.

* Enhances understanding of spatial orientation by using visual elements like a turning car model, radar view, and live data tables.

## How to Test
To run and test this project locally:
1. Connect LIDAR Sensor

* Ensure the LIDAR device is connected to your PC via TCP/IP.

* Confirm the IP address and port are correctly set in the Python script.

2. Install Dependencies
* pip install flask
3. Start the Flask App
* python app.py
4. Open the Dashboard
* Open your browser and go to: http://localhost:5000
* You will see:
  * A live radar chart
  * Steering angle car model
  * Real-time data table (angle, distance, intensity)

5. Interact with the System
* Rotate the steering (simulated or real) and see the car's front wheels turn accordingly.
* Watch LIDAR data update as the sensor scans the environment.

## GUI Preview
https://github.com/user-attachments/assets/99f4d5ca-f5d9-41b6-b825-d5514eaff5aa
