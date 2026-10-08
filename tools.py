from datetime import datetime, timedelta

def get_expiration_date(ingredient: str):
    """
    Calculates the real expiration date based on today's date.
    """
    # A simple database of shelf life in days
    shelf_life = {
        "spinach": 5,
        "chicken": 2,
        "milk": 7,
        "tomato": 6,
        "rice": 180
    }
    
    ingredient_lower = ingredient.lower()
    
    if ingredient_lower in shelf_life:
        days_left = shelf_life[ingredient_lower]
        expiration = datetime.now() + timedelta(days=days_left)
        return f"{ingredient} expires in {days_left} days (on {expiration.strftime('%Y-%m-%d')})."
    else:
        return f"Unknown ingredient. Assume it needs to be used within 3 days."