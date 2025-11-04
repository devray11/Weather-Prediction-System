from flask import Flask, render_template, jsonify
import requests
from datetime import datetime
from alert_system import EnvironmentalAlertSystem
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ThingSpeak credentials
THINGSPEAK_READ_API_KEY = "28GTEFBHR69BVSF2"
THINGSPEAK_CHANNEL_ID = "3057233"


class ThingSpeakDataManager:
    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.latest_data = {
            'temperature': 24.0,
            'humidity': 65.0,
            'gas_level': 150.0,
            'timestamp': datetime.now().isoformat(),
            'status': 'disconnected'
        }
        self.alert_system = EnvironmentalAlertSystem()

    def safe_float_parse(self, value, default=0.0):
        """Safely parse string/None to float, else return default"""
        try:
            if value is None or value == '':
                return default
            return float(value)
        except Exception:
            return default

    def fetch_latest_data(self):
        """Fetch latest data from ThingSpeak"""
        url = f"https://api.thingspeak.com/channels/{self.channel_id}/feeds.json"
        params = {'api_key': self.api_key, 'results': 1}

        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if 'feeds' in data and len(data['feeds']) > 0:
                    latest = data['feeds'][0]
                    self.latest_data = {
                        'temperature': self.safe_float_parse(latest.get('field1')),
                        'humidity': self.safe_float_parse(latest.get('field2')),
                        'gas_level': self.safe_float_parse(latest.get('field3')),
                        'timestamp': latest.get('created_at', datetime.now().isoformat()),
                        'status': 'connected'
                    }
                    logging.info(f"✅ Data updated: {self.latest_data}")
                    return True
                else:
                    logging.warning("⚠️ No data available in ThingSpeak feed")
                    self.latest_data['status'] = 'no_data'
                    return False
            else:
                logging.error(f"❌ ThingSpeak API error: {r.status_code}")
                self.latest_data['status'] = 'api_error'
                return False

        except Exception as e:
            logging.error(f"🚨 ThingSpeak data fetch error: {e}")
            self.latest_data['status'] = 'error'
            return False


# Initialize ThingSpeak manager
data_manager = ThingSpeakDataManager(THINGSPEAK_READ_API_KEY, THINGSPEAK_CHANNEL_ID)


@app.route('/')
def index():
    """Serve frontend"""
    return render_template('index.html')


@app.route('/api/current-data')
def current_data():
    """Return latest sensor data + ML prediction"""
    if data_manager.fetch_latest_data():
        data = data_manager.latest_data.copy()

        # Run ML model prediction if available
        try:
            ml_pred = data_manager.alert_system.predict_condition(
                data['temperature'], data['humidity'], data['gas_level']
            )
            if ml_pred:
                data['ml_prediction'] = ml_pred
        except Exception as e:
            logging.error(f"ML prediction error: {e}")

        return jsonify({'success': True, 'data': data})

    # If fetch failed, return last known data
    return jsonify({'success': False, 'data': data_manager.latest_data}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
