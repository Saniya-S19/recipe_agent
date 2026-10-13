from datetime import datetime, timedelta
import requests

def get_expiration_date(ingredient: str):
    """
    Calculates the real expiration date based on today's date.
    """
    # Expanded database of shelf life in days
    shelf_life = {
        "spinach": 5,
        "chicken": 2,
        "milk": 7,
        "tomato": 6,
        "rice": 180,
        "onion": 30,
        "garlic": 150,
        "potato": 30,
        "eggs": 21,
        "bread": 5
    }
    
    ingredient_lower = ingredient.lower()
    
    if ingredient_lower in shelf_life:
        days_left = shelf_life[ingredient_lower]
        expiration = datetime.now() + timedelta(days=days_left)
        return f"{ingredient} expires in {days_left} days (on {expiration.strftime('%Y-%m-%d')})."
    else:
        return f"Unknown ingredient. Assume it needs to be used within 3 days."

def get_nutritional_info(ingredient: str):
    """
    Fetches live nutritional data from the Open Food Facts API.
    """
    # The public search endpoint for Open Food Facts
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={ingredient}&search_simple=1&action=process&json=1&page_size=1"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Check if the API found any matching products
        if data.get("products"):
            product = data["products"][0]
            nutriments = product.get("nutriments", {})
            
            # Extract macros per 100g
            energy = nutriments.get("energy-kcal_100g", "N/A")
            proteins = nutriments.get("proteins_100g", "N/A")
            carbs = nutriments.get("carbohydrates_100g", "N/A")
            fat = nutriments.get("fat_100g", "N/A")
            
            return f"Live nutrition per 100g of {ingredient}: {energy} kcal, {proteins}g Protein, {carbs}g Carbs, {fat}g Fat."
        else:
            return f"Could not find live nutrition data for {ingredient}. Assume standard macros."
            
    except Exception as e:
        return f"API Connection Error: {str(e)}"

def get_time_of_day():
    """
    Checks the current system time to provide meal context.
    """
    current_hour = datetime.now().hour
    
    if current_hour < 11:
        return "Context: It is morning. Recommend breakfast."
    elif current_hour < 16:
        return "Context: It is afternoon. Recommend lunch."
    elif current_hour < 21:
        return "Context: It is evening. Recommend dinner."
    else:
        return "Context: It is late night. Recommend a light, easy-to-digest midnight snack."