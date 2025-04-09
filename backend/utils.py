import math
import random
import json

def calculate_sample_size(block, plan):
    """
    Calculate the sample size for a block based on the plan parameters.
    This is a simplified calculation - you should replace with your actual algorithm.
    """
    # Get block area in hectares (assuming area is stored in hectares)
    block_area = block.area or 1.0  # Default to 1 hectare if area is not set
    
    # Ensure detection confidence and design prevalence are valid
    detection_confidence = max(0.01, min(0.99, plan.detectionConfidence))
    design_prevalence = max(0.01, min(0.99, plan.designPrevalence))
    
    # Calculate base sample size using design prevalence and detection confidence
    # This is a simplified formula - replace with your actual calculation
    try:
        base_sample = math.ceil(
            (1 - math.log(1 - detection_confidence)) / 
            (1 - math.log(1 - design_prevalence))
        )
    except (ValueError, ZeroDivisionError):
        # Fallback to a simple calculation if the formula fails
        base_sample = math.ceil(1 / design_prevalence)
    
    # Adjust sample size based on block area
    # Assuming we want at least 1 sample per hectare, with diminishing returns
    area_factor = math.sqrt(block_area)
    sample_size = max(base_sample, math.ceil(area_factor))
    
    # Apply observer detection probability adjustment
    observer_prob = max(0.1, min(1.0, plan.observerDetectionProb))
    if observer_prob < 1.0:
        sample_size = math.ceil(sample_size / observer_prob)
        
    return max(1, sample_size)  # Ensure at least 1 sample

def generate_recommendations(block, sample_size):
    """
    Generate recommendations for sampling this block.
    Returns a JSON string with recommendations.
    """
    recommendations = {
        "sampling_strategy": "Systematic sampling",
        "sample_size": sample_size,
        "sampling_points": [],
        "notes": f"Sample {sample_size} plants from block {block.name}"
    }
    
    # If block has location points, generate sampling points
    if hasattr(block, 'location_point_1') and block.location_point_1:
        # This is a simplified approach - replace with your actual algorithm
        # for generating sampling points based on block geometry
        for i in range(min(sample_size, 10)):  # Limit to 10 points for example
            try:
                lat = float(block.location_point_1.split(',')[0]) + random.uniform(-0.001, 0.001)
                lng = float(block.location_point_1.split(',')[1]) + random.uniform(-0.001, 0.001)
                recommendations["sampling_points"].append({
                    "id": f"SP{i+1}",
                    "latitude": lat,
                    "longitude": lng
                })
            except (ValueError, IndexError):
                # Skip this point if there's an error parsing the coordinates
                continue
    
    return json.dumps(recommendations)

