
# Flight Delay Prediction Model - Usage Documentation

## Model Overview
- **Model Type**: Logistic Regression
- **Accuracy**: 80.1%
- **Training Data**: 271,940 flight records from 2013
- **Features**: Day of Week, Origin Airport
- **Target**: Flight delay > 15 minutes

## Installation Requirements
```python
import pickle
```

## Basic Usage

### 1. Load the Model
```python
import pickle

# Load the complete model with metadata
with open('model.pkl', 'rb') as f:
    model_data = pickle.load(f)

model = model_data['model_object']
```

### 2. Make Predictions
```python
# Example: Predict delay for Monday (1) at Airport ID 10
day_of_week = 1  # 1=Monday, 2=Tuesday, ..., 7=Sunday
airport_id = 10  # Airport ID (1-70)

# Make prediction
prediction = model.predict([[day_of_week, airport_id]])[0]
probabilities = model.predict_proba([[day_of_week, airport_id]])[0]

# Results
is_delayed = prediction == 1
delay_probability = probabilities[1]
```

### 3. Using the Helper Function
```python
result = predict_flight_delay(day_of_week=1, origin_airport_id=10)
print(result)
```

## Input Specifications
- **day_of_week**: Integer 1-7 (1=Monday, 7=Sunday)
- **origin_airport_id**: Integer 1-70 (encoded airport identifier)

## Output Format
```python
{
    'input': {
        'day_of_week': 1,
        'origin_airport_id': 10
    },
    'prediction': {
        'is_delayed': False,
        'delay_probability': 0.199,
        'no_delay_probability': 0.801
    },
    'model_info': {
        'model_type': 'Logistic Regression',
        'accuracy': 0.801,
        'version': '1.0'
    },
    'status': 'success'
}
```

## Model Files
- **model.pkl**: Complete model with metadata (recommended)
- **model.joblib**: Alternative format using joblib
- **model_object.pkl**: Model object only (lightweight)

## Performance Characteristics
- **Accuracy**: 80.1%
- **Precision**: 0.0% (due to class imbalance)
- **Recall**: 0.0% (model predicts majority class)
- **F1-Score**: 0.0%
- **Use Case**: General delay probability estimation

## Limitations
- Model trained on 2013 data - may need updating for current patterns
- Class imbalance leads to conservative predictions
- Limited to 2 features - airport and day of week only
- Does not account for weather, airline, or seasonal factors
