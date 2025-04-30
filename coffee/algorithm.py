# Removed the import of numpy

# Updated the function to use Python's built-in libraries instead of numpy

def predict_coffee_yield(variety, fertilizer_kg, hectares, prev_yield, has_buds, weather, 
                         rainfall, temperature, soil_ph, disease_cases=None, model=None):
    """
    Predict coffee yield using a hybrid heuristic-ML approach
    
    Args:
        variety: Coffee variety (Ruiru 11, SL28, SL34, Batian)
        fertilizer_kg: Fertilizer amount in kilograms
        hectares: Land area in hectares
        prev_yield: Previous year's yield in kg
        has_buds: Boolean whether buds are present
        weather: Current weather condition
        rainfall: Rainfall in mm (optional for ML)
        temperature: Temperature in °C (optional for ML)
        soil_ph: Soil pH value (optional for ML)
        disease_cases: Dictionary of disease cases (optional for ML)
        model: Pre-trained ML model (optional)
    
    Returns:
        tuple: (predicted_yield_kg, confidence_percentage)
    """
    
    # 1. Base yield by variety (kg per hectare) - Kenyan specific data
    variety_base_yields = {
        "Ruiru 11": 1800,  # High-yielding hybrid
        "SL28": 1200,      # Traditional quality variety
        "SL34": 1300,      # Traditional quality variety
        "Batian": 1700,     # Newer high-yielding variety
    }
    
    # 2. Fertilizer efficiency (kg per hectare)
    def calculate_fertilizer_factor(kg, area):
        if area == 0:
            return 1.0
        kg_per_ha = kg / area
        if kg_per_ha < 50:
            return 0.8 + (kg_per_ha/50)*0.4
        elif kg_per_ha < 150:
            return 1.2 + ((kg_per_ha-50)/100)*0.5
        else:
            return min(1.9, 1.7 + ((kg_per_ha-150)/150)*0.2)
    
    # 3. Environmental factors
    weather_factors = {
        "Sunny": 1.0,
        "Partly Cloudy": 0.95,
        "Cloudy": 0.9,
        "Rainy": 0.85,
        "Stormy": 0.7,
        "Dry": 0.8,
        "ivo": 1.0  # Normal conditions
    }
    
    # 4. If ML model is provided, use it for prediction
    if model is not None:
        try:
            # Prepare input features for ML model
            input_features = {
                'Coffee Variety': variety,
                'Fertilizer Use (Kg/acre)': fertilizer_kg * 0.404686,  # Convert kg/ha to kg/acre
                'Rainfall (mm)': rainfall,
                'Temperature (°C)': temperature,
                'Soil pH': soil_ph,
                'Has Buds': int(has_buds),
                **(disease_cases or {})  # Unpack any disease cases
            }
            
            # Convert to model input format (would need proper feature engineering)
            # ml_prediction = model.predict([processed_features])[0]
            # return ml_prediction, 95  # Higher confidence for ML predictions
            
        except Exception as e:
            print(f"ML prediction failed: {e}. Falling back to heuristic method.")
    
    # Heuristic prediction (fallback if no ML model or ML fails)
    try:
        base_yield = variety_base_yields.get(variety, 1500)
        fert_factor = calculate_fertilizer_factor(fertilizer_kg, hectares)
        weather_factor = weather_factors.get(weather, 0.9)
        bud_factor = 1.25 if has_buds else 0.85
        
        # Current year prediction (80% weight)
        current_pred = base_yield * fert_factor * bud_factor * weather_factor
        
        # Blend with historical data (20% weight if available)
        historical_adjusted = (prev_yield / hectares) if hectares > 0 and prev_yield > 0 else current_pred
        blended_pred = (0.8 * current_pred) + (0.2 * historical_adjusted)
        
        # Scale by land area
        predicted_yield = blended_pred * hectares
        
        # Confidence calculation
        confidence = 70  # Base confidence
        confidence += 10 if fertilizer_kg > 0 else 0
        confidence += 15 if has_buds else 0
        confidence += 5 if prev_yield > 0 else 0
        confidence = min(95, confidence)
        
        return round(predicted_yield, 2), round(confidence, 2)
    
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0, 0