import os
from django.shortcuts import render
import json
import joblib  # For loading the trained model
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Get the grandparent directory of the current directory
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
print(f"Grandparent directory: {grandparent_dir}")

# Load the trained model (replace 'decision_tree_model' with your model's filename)
model_path = os.path.join(grandparent_dir, 'decision_tree_model')
print(f"Model path: {model_path}")
model = joblib.load(model_path)

@api_view(['POST'])
def predict_performance(request):
    try:
        # Parse input data from the POST request
        input_data = json.loads(request.body)
        
        # Extract features (ensure keys match your training dataset)
        features = [
            input_data['G1'],
            input_data['G2'],
            input_data['studytime'],
            input_data['absences'],
            input_data['avg_grade']
        ]
        
        # Reshape input and make prediction
        prediction = model.predict([features])[0]
        
        # Return the prediction as a JSON response
        return JsonResponse({'prediction': prediction}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
