import os
import joblib
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Define model, features, and scaler file paths
MODEL_FILENAME = 'decision_tree_model.pkl'
FEATURES_FILENAME = 'feature_names.pkl'
SCALER_FILENAME = 'scaler.pkl'
LABEL_ENCODER_FILENAME = 'label_encoder.pkl'

MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', MODEL_FILENAME)
FEATURES_PATH = os.path.join(settings.BASE_DIR, 'models', FEATURES_FILENAME)
SCALER_PATH = os.path.join(settings.BASE_DIR, 'models', SCALER_FILENAME)
LABEL_ENCODER_PATH = os.path.join(settings.BASE_DIR, 'models', LABEL_ENCODER_FILENAME)

# Load the trained model
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully.")
except Exception as e:
    raise FileNotFoundError(f"❌ Failed to load the model. Ensure it exists at {MODEL_PATH}: {e}")

# Load feature names
try:
    feature_names = joblib.load(FEATURES_PATH)
    print(f"✅ Feature Names Loaded: {feature_names}")
except Exception as e:
    feature_names = None
    print(f"❌ Failed to load feature names: {e}")

# Load the scaler
try:
    scaler = joblib.load(SCALER_PATH)
    print("✅ Scaler loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load scaler: {e}")
    scaler = None

# Load the label encoder
try:
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    print(f"✅ LabelEncoder loaded successfully. Classes: {label_encoder.classes_}")
except Exception as e:
    print(f"❌ Failed to load label encoder: {e}")
    label_encoder = None

@api_view(['POST'])
def predict_performance(request):
    try:
        # Ensure model has feature names
        model_features = getattr(model, "feature_names_in_", None)
        
        if model_features is None:
            if feature_names:
                model_features = feature_names  # Use loaded feature names if available
                print("⚠️ Using manually loaded feature names.")
            else:
                return JsonResponse({'error': 'Model does not store feature names. Ensure training used a DataFrame.'}, status=400)

        print(f"✅ Model Feature Names: {model_features}")

        # Parse JSON input
        input_data = JSONParser().parse(request)
        print(f"✅ Received Input Data: {input_data}")

        # Validate and extract feature values
        missing_features = [f for f in model_features if f not in input_data]
        if missing_features:
            return JsonResponse({'error': f'Missing required inputs: {missing_features}'}, status=400)

        # Convert input data to NumPy array for prediction
        try:
            features = np.array([input_data[f] for f in model_features], dtype=float).reshape(1, -1)
        except ValueError as e:
            return JsonResponse({'error': f'Invalid input values: {e}'}, status=400)

        print(f"✅ Final Feature Array for Prediction: {features}")

        # Apply scaling if scaler exists
        if scaler:
            features = scaler.transform(features)
            print(f"✅ Scaled Feature Array: {features}")
        else:
            print("⚠️ No scaler found. Proceeding without scaling.")

        # Make prediction
        prediction = model.predict(features)[0]

        # Convert numeric prediction to categorical if label encoder exists
        if label_encoder:
            try:
                prediction_label = label_encoder.inverse_transform([prediction])[0].capitalize()
                print(f"✅ Decoded Prediction: {prediction_label}")
            except ValueError:
                return JsonResponse({'error': f'Unexpected prediction value: {prediction}'}, status=400)
        else:
            prediction_label = str(prediction)
            print("⚠️ No label encoder found. Returning numeric prediction.")

        return JsonResponse({'prediction': prediction_label}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON input. Send a valid JSON request.'}, status=400)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return JsonResponse({'error': f'Unexpected error: {e}'}, status=500)
