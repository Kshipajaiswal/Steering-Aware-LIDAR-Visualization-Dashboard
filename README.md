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

## 🛠Tech Stack
* Backend: Python, Flask
* Frontend: HTML, CSS, JavaScript
* Data Source: LIDAR Sensor
* Charting: Custom Radar Chart

## GUI Preview
https://github.com/user-attachments/assets/99f4d5ca-f5d9-41b6-b825-d5514eaff5aa
