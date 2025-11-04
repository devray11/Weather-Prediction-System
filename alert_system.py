"""
Alert System Module for Environmental Monitoring
Author: Environmental Monitoring System
Date: September 2025
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import joblib
import numpy as np
import os

# ======================
# Threshold Configuration
# ======================
TEMP_UPPER_THRESHOLD = 35.0
TEMP_LOWER_THRESHOLD = 5.0
HUMIDITY_UPPER_THRESHOLD = 85.0
HUMIDITY_LOWER_THRESHOLD = 20.0
GAS_PPM_THRESHOLD = 500.0

# ======================
# Email Configuration
# ======================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "2022002393.gcet@cvmu.edu.in"   # Replace with your email
SENDER_PASSWORD = "usfc muzw jzdx oyrw"        # Replace with your Gmail app password
DEFAULT_RECIPIENT = "devmray112004@gmail.com"  # Replace with recipient email

# ======================
# Alert Templates
# ======================
ALERT_TEMPLATES = {
    'high_temperature': "🔥 HIGH TEMPERATURE ALERT!\n\nCurrent temperature: {temp}°C\nThreshold: {threshold}°C\nLocation: Environmental Monitoring Station\nTime: {timestamp}",
    'low_temperature': "🧊 LOW TEMPERATURE ALERT!\n\nCurrent temperature: {temp}°C\nThreshold: {threshold}°C\nLocation: Environmental Monitoring Station\nTime: {timestamp}",
    'high_humidity': "💧 HIGH HUMIDITY ALERT!\n\nCurrent humidity: {humidity}%\nThreshold: {threshold}%\nLocation: Environmental Monitoring Station\nTime: {timestamp}",
    'low_humidity': "🏜️ LOW HUMIDITY ALERT!\n\nCurrent humidity: {humidity}%\nThreshold: {threshold}%\nLocation: Environmental Monitoring Station\nTime: {timestamp}",
    'poor_air_quality': "⚠️ POOR AIR QUALITY ALERT!\n\nCurrent gas level: {gas_level} PPM\nThreshold: {threshold} PPM\nLocation: Environmental Monitoring Station\nTime: {timestamp}",
    'ml_prediction': "🤖 ML PREDICTION ALERT!\n\nPredicted condition: {condition}\nConfidence: {confidence:.2%}\nCurrent readings:\n- Temperature: {temp}°C\n- Humidity: {humidity}%\n- Gas Level: {gas_level} PPM\nTime: {timestamp}"
}

# ======================
# Alert System Class
# ======================
class EnvironmentalAlertSystem:
    def __init__(self,
                 smtp_server=SMTP_SERVER,
                 smtp_port=SMTP_PORT,
                 sender_email=SENDER_EMAIL,
                 sender_password=SENDER_PASSWORD,
                 model_file='environment_model.joblib'):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.ml_model = None
        self.model_file = model_file

        # Load ML model if available
        try:
            self.load_ml_model()
        except Exception as e:
            print(f"⚠️ Warning: ML model not loaded ({e}). Threshold alerts only.")

    # ----------------------
    # Load ML Model
    # ----------------------
    def load_ml_model(self):
        if not os.path.exists(self.model_file):
            raise FileNotFoundError(f"ML model file '{self.model_file}' not found.")
        model_package = joblib.load(self.model_file)
        self.ml_model = {
            'model': model_package['model'],
            'scaler': model_package['scaler'],
            'label_encoder': model_package['label_encoder'],
            'feature_columns': model_package['feature_columns']
        }
        print("✅ ML model loaded successfully.")

    # ----------------------
    # Predict Condition (ML)
    # ----------------------
    def predict_condition(self, temperature, humidity, gas_level):
        if not self.ml_model:
            return None
        try:
            now = datetime.now()
            hour = now.hour
            day_of_year = now.timetuple().tm_yday
            month = now.month

            # Feature engineering (MUST match training)
            temp_humidity_ratio = temperature / (humidity + 1e-6)
            comfort_index = temperature * 0.7 + humidity * 0.3
            gas_level_normalized = gas_level / 1000.0  # adjust scale if dataset differs

            features = np.array([[
                temperature, humidity, gas_level,
                hour, day_of_year, month,
                temp_humidity_ratio, comfort_index, gas_level_normalized
            ]])

            features_scaled = self.ml_model['scaler'].transform(features)
            prediction = self.ml_model['model'].predict(features_scaled)[0]
            prediction_proba = self.ml_model['model'].predict_proba(features_scaled)[0]

            condition = self.ml_model['label_encoder'].inverse_transform([prediction])[0]
            confidence = float(prediction_proba[prediction])

            return {'condition': condition, 'confidence': confidence}
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            return None

    # ----------------------
    # Email Alerts
    # ----------------------
    def send_alert_email(self, recipient_email, subject, body):
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            txt = MIMEText(body, "plain")
            message.attach(txt)

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            print(f"📩 Alert email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False

    # ----------------------
    # Threshold Violations
    # ----------------------
    def check_thresholds(self, temperature, humidity, gas_level):
        violations = []
        if temperature > TEMP_UPPER_THRESHOLD:
            violations.append({'type': 'high_temperature', 'value': temperature, 'threshold': TEMP_UPPER_THRESHOLD})
        elif temperature < TEMP_LOWER_THRESHOLD:
            violations.append({'type': 'low_temperature', 'value': temperature, 'threshold': TEMP_LOWER_THRESHOLD})

        if humidity > HUMIDITY_UPPER_THRESHOLD:
            violations.append({'type': 'high_humidity', 'value': humidity, 'threshold': HUMIDITY_UPPER_THRESHOLD})
        elif humidity < HUMIDITY_LOWER_THRESHOLD:
            violations.append({'type': 'low_humidity', 'value': humidity, 'threshold': HUMIDITY_LOWER_THRESHOLD})

        if gas_level > GAS_PPM_THRESHOLD:
            violations.append({'type': 'poor_air_quality', 'value': gas_level, 'threshold': GAS_PPM_THRESHOLD})

        return violations

    # ----------------------
    # Main Monitoring Logic
    # ----------------------
    def monitor_and_alert(self, temperature, humidity, gas_level, recipient_email=DEFAULT_RECIPIENT):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alerts_sent = []

        # Threshold checks
        violations = self.check_thresholds(temperature, humidity, gas_level)
        for violation in violations:
            alert_type = violation['type']
            template = ALERT_TEMPLATES.get(alert_type, "")
            subject, message = "", ""

            if alert_type in ['high_temperature', 'low_temperature']:
                message = template.format(temp=temperature, threshold=violation['threshold'], timestamp=timestamp)
                subject = f"Temperature Alert: {temperature}°C"
            elif alert_type in ['high_humidity', 'low_humidity']:
                message = template.format(humidity=humidity, threshold=violation['threshold'], timestamp=timestamp)
                subject = f"Humidity Alert: {humidity}%"
            elif alert_type == 'poor_air_quality':
                message = template.format(gas_level=gas_level, threshold=violation['threshold'], timestamp=timestamp)
                subject = f"Air Quality Alert: {gas_level} PPM"

            if subject and self.send_alert_email(recipient_email, subject, message):
                alerts_sent.append(alert_type)

        # ML-based alerts
        ml_pred = self.predict_condition(temperature, humidity, gas_level)
        if ml_pred and ml_pred['condition'] in ['Poor Air Quality', 'Foggy'] and ml_pred['confidence'] > 0.8:
            ml_message = ALERT_TEMPLATES['ml_prediction'].format(
                condition=ml_pred['condition'],
                confidence=ml_pred['confidence'],
                temp=temperature,
                humidity=humidity,
                gas_level=gas_level,
                timestamp=timestamp)
            ml_subject = f"ML Alert: {ml_pred['condition']}"
            if self.send_alert_email(recipient_email, ml_subject, ml_message):
                alerts_sent.append('ml_prediction')

        return {
            'timestamp': timestamp,
            'readings': {'temperature': temperature, 'humidity': humidity, 'gas_level': gas_level},
            'violations': violations,
            'ml_prediction': ml_pred,
            'alerts_sent': alerts_sent,
            'total_alerts': len(alerts_sent)
        }
