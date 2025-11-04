# IoT-Based Environmental Monitoring System

## Machine Learning-Enhanced Monitoring with Predictive Alerts

This repository contains a cost-effective, IoT-based environmental monitoring system enhanced with machine learning for real-time prediction and automated alerts. This project addresses the limitations of traditional, costly weather stations by providing an affordable and efficient solution for localized environmental monitoring.

The system uses an ESP8266 microcontroller with DHT11 and MQ-135 sensors to measure real-time temperature, humidity, and air quality index (AQI). This data is continuously transmitted to the ThingSpeak cloud platform for aggregation and storage. A Random Forest machine learning model analyzes the live data to predict environmental conditions (e.g., 'Normal', 'Hot', 'Cold', 'Foggy', 'Poor Air Quality').

The project features a responsive web application for data visualization and a dual-alert mechanism that automatically triggers email notifications for both predefined threshold violations and ML-driven predictive warnings.

## Features

* **Real-Time Data Collection:** Utilizes an ESP8266 microcontroller, DHT11 (temperature, humidity), and MQ-135 (air quality) sensors.
* **Cloud IoT Integration:** Transmits and logs sensor data to the ThingSpeak cloud platform for analysis and visualization.
* **ML-Powered Predictions:** Employs a trained Random Forest model to accurately classify the current environmental condition.
* **Dual Alert Mechanism:** Sends automated email alerts based on (1) simple threshold violations and (2) machine learning-based predictions of adverse conditions.
* **Responsive Web Dashboard:** A clean web interface to visualize live sensor readings and the ML model's predictions in real-time.

## Technologies Used

* **Hardware:** ESP8266, DHT11 Sensor, MQ-135 Sensor
* **Cloud Platform:** ThingSpeak
* **Backend & ML:** Python, Flask, Scikit-learn (RandomForestClassifier)
* **Frontend:** HTML, CSS, JavaScript
* **Alerting:** smtplib (Python for email notifications)
![Dashboard](https://github.com/devray11/Weather-Prediction-System/blob/c577f105b79f6d6235a9a881cac3c69a35fe9024/Dashboard.png)

![Weather Prediction System Images](https://github.com/devray11/Weather-Prediction-System/blob/a786df20c4698202326139631538938e9b90f364/Weather-Prediction-System-Images.png)

