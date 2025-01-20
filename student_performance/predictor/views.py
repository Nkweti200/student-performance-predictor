import os
import json
import joblib
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Get the grandparent directory of the current directory
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)

# Load the trained model
model_path = os.path.join(grandparent_dir, 'decision_tree_model')
try:
    model = joblib.load(model_path)
    print("Model loaded successfully.")
except Exception as e:
    raise FileNotFoundError(f"Failed to load the model. Ensure the model exists at {model_path}: {e}")

@api_view(['POST'])
def predict_performance(request):
    try:
        # Parse input data
        input_data = json.loads(request.body)
        
        # Validate model feature names
        try:
            feature_names = model.feature_names_in_
        except AttributeError:
            return JsonResponse({'error': 'Model does not store feature names. Check consistency in input features.'}, status=400)
        
        # Extract features dynamically
        features = []
        for feature in feature_names:
            if feature not in input_data:
                return JsonResponse({'error': f'Missing required input: {feature}'}, status=400)
            features.append(input_data[feature])
        
        # Convert to numeric and reshape
        features = np.array(features, dtype=float).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features)[0]
        print(f"Prediction result: {prediction}")

        return JsonResponse({'prediction': prediction}, status=200)
    
    except json.JSONDecodeError:
        print("Error: Invalid JSON input")
        return JsonResponse({'error': 'Invalid JSON input. Please send valid JSON.'}, status=400)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
