import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
import joblib
from datetime import datetime

class EnvironmentalModelTrainer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.classes_ = None

    def load_and_preprocess_data(self, csv_file_path):
        print("Loading environmental dataset...")
        df = pd.read_csv(csv_file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        df['month'] = df['timestamp'].dt.month
        df['temperature_humidity_ratio'] = df['temperature_celsius'] / (df['humidity_percent'] + 1e-6)
        df['comfort_index'] = df['temperature_celsius'] * 0.7 + df['humidity_percent'] * 0.3
        df['gas_level_normalized'] = (df['gas_level_ppm'] - df['gas_level_ppm'].min()) / \
                                     (df['gas_level_ppm'].max() - df['gas_level_ppm'].min())
        self.feature_columns = ['temperature_celsius', 'humidity_percent', 'gas_level_ppm', 
                                'hour_of_day', 'day_of_year', 'month', 'temperature_humidity_ratio',
                                'comfort_index', 'gas_level_normalized']
        X = df[self.feature_columns].copy()
        y = df['condition_label'].copy()
        imputer = SimpleImputer(strategy='mean')
        X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        self.classes_ = self.label_encoder.classes_
        print(f"Features shape: {X.shape}")
        print(f"Target classes: {list(self.label_encoder.classes_)}")
        return X, y_encoded

    def train_model(self, X, y):
        print("\nTraining Random Forest Classifier...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.model = RandomForestClassifier(n_estimators=200, max_depth=20,
                                            min_samples_split=5, min_samples_leaf=2,
                                            max_features='sqrt', bootstrap=True,
                                            class_weight='balanced', random_state=42, n_jobs=-1)
        self.model.fit(X_train_scaled, y_train)
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, target_names=self.label_encoder.classes_, output_dict=True)
        print(f"Training Accuracy: {accuracy:.4f}")
        print(classification_report(y_test, y_pred, target_names=self.label_encoder.classes_))
        feat_importance = pd.DataFrame({'feature': self.feature_columns, 'importance': self.model.feature_importances_}).sort_values('importance', ascending=False)
        print("\nFeature importance:")
        print(feat_importance)
        return {'accuracy': accuracy, 'classification_report': class_report, 'feature_importance': feat_importance}

    def save_model(self, model_filename='environment_model.joblib'):
        if self.model is None:
            raise ValueError("Train model first")
        model_package = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'classes': self.classes_,
            'training_timestamp': datetime.now().isoformat()
        }
        joblib.dump(model_package, model_filename)
        print(f"Model saved as {model_filename}")

# Use inside main app script or standalone script
if __name__ == "__main__":
    trainer = EnvironmentalModelTrainer()
    X, y = trainer.load_and_preprocess_data('environmental_data.csv')
    results = trainer.train_model(X, y)
    trainer.save_model()
