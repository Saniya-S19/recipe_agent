import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_expiration_date, get_nutritional_info, get_time_of_day 

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. MEMORY SETUP: We move the history outside the function so it survives between questions
system_prompt = """
You are a Zero-Waste Culinary Assistant. Your goal is to suggest meals that prioritize using the user's expiring ingredients, while factoring in their nutritional needs and the current time of day. 

You MUST always reply in valid JSON format using exactly these keys: "recipe_name", "meal_type", "expiring_ingredients", "nutrition_notes", and "instructions". Do not include any conversational text before or after the JSON.
"""

chat_memory = [
    {"role": "system", "content": system_prompt}
]

def agent_loop(user_input: str):
    # 2. Add the user's newest prompt to the ongoing memory
    chat_memory.append({"role": "user", "content": user_input})
    
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
        {
            "type": "function",
            "function": {
                "name": "get_time_of_day",
                "description": "Checks the current time to recommend appropriate meals.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    print("\n[Agent Thinking...]")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_memory,  # 3. Pass the full memory to the model
        tools=agent_tools,
        temperature=0.3 
    )
    
    response_message = response.choices[0].message

    if response_message.tool_calls:
        chat_memory.append(response_message)
        
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
                
            elif function_name == "get_time_of_day":
                print(f"[Running Tool] Checking the current time of day...")
                tool_result = get_time_of_day()
                
            chat_memory.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": tool_result
            })
        
        print("[Agent Generating Final Recipe...]")
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_memory,
            temperature=0.3
        )
        
        final_answer = second_response.choices[0].message.content
        # 4. Save the agent's final answer to memory so it remembers what it told you
        chat_memory.append({"role": "assistant", "content": final_answer})
        return final_answer
        
    final_answer = response_message.content
    # Save the agent's final answer to memory
    chat_memory.append({"role": "assistant", "content": final_answer})
    return final_answer

if __name__ == "__main__":
    print("Welcome to the Context-Aware Culinary Agent. Type 'exit' to quit.")
    while True:
        user_query = input("\nWhat are we solving for today? > ")
        if user_query.lower() == 'exit':
            break
        
        answer = agent_loop(user_query)
        
        try:
            clean_answer = answer.replace('```json', '').replace('```', '').strip()
            recipe_data = json.loads(clean_answer)
            
            print("\n" + "="*40)
            print(f"🍽️  RECIPE: {recipe_data.get('recipe_name', 'Chef\\'s Special')}")
            print(f"🕒  MEAL TYPE: {recipe_data.get('meal_type', 'Any')}")
            print(f"⚠️  EXPIRING: {', '.join(recipe_data.get('expiring_ingredients', []))}")
            print(f"💪  NUTRITION: {recipe_data.get('nutrition_notes', 'N/A')}")
            print("-" * 40)
            print(f"📖  INSTRUCTIONS:\n{recipe_data.get('instructions', 'N/A')}")
            print("="*40 + "\n")
            
        except json.JSONDecodeError:
            print(f"\n[Raw Agent Response]:\n{answer}")