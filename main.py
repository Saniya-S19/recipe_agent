import os
import json
from dotenv import load_dotenv
from openai import OpenAI
# 1. Import the new time tool
from tools import get_expiration_date, get_nutritional_info, get_time_of_day 

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def agent_loop(user_input: str):
    system_prompt = """
    You are a Zero-Waste Culinary Assistant. Your goal is to suggest meals that prioritize using the user's expiring ingredients, while factoring in their nutritional needs and the current time of day. 
    
    You MUST always reply in valid JSON format using exactly these keys: "recipe_name", "meal_type", "expiring_ingredients", "nutrition_notes", and "instructions". Do not include any conversational text before or after the JSON.
    """
    
    agent_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_expiration_date",
                "description": "Calculates how many days until an ingredient expires.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ingredient": {"type": "string", "description": "The ingredient name"}
                    },
                    "required": ["ingredient"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_nutritional_info",
                "description": "Returns the nutritional profile (protein, carbs, fat) of an ingredient.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ingredient": {"type": "string", "description": "The ingredient name"}
                    },
                    "required": ["ingredient"]
                }
            }
        },
        # 2. Add the instruction manual for the time tool (Notice it has empty properties because it doesn't need input)
        {
            "type": "function",
            "function": {
                "name": "get_time_of_day",
                "description": "Checks the current time to recommend appropriate meals (breakfast, lunch, dinner, or late-night snacks).",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    print("\n[Agent Thinking...]")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=agent_tools,
        temperature=0.3 
    )
    
    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            if function_name == "get_expiration_date":
                ingredient = arguments.get("ingredient")
                print(f"[Running Tool] Checking expiration for {ingredient}...")
                tool_result = get_expiration_date(ingredient)
                
            elif function_name == "get_nutritional_info":
                ingredient = arguments.get("ingredient")
                print(f"[Running Tool] Fetching nutrition for {ingredient}...")
                tool_result = get_nutritional_info(ingredient)
                
            # 3. Handle the execution of the new time tool
            elif function_name == "get_time_of_day":
                print(f"[Running Tool] Checking the current time of day...")
                tool_result = get_time_of_day()
                
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": tool_result
            })
        
        print("[Agent Generating Final Recipe...]")
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3
        )
        return second_response.choices[0].message.content
        
    return response_message.content

if __name__ == "__main__":
    print("Welcome to the Context-Aware Culinary Agent. Type 'exit' to quit.")
    while True:
        user_query = input("\nWhat are we solving for today? > ")
        if user_query.lower() == 'exit':
            break
        answer = agent_loop(user_query)
        print(f"\n[Agent Action/Response]:\n{answer}")