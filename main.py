import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_expiration_date

# Load environment variables
load_dotenv()

# Initialize the LLM client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def agent_loop(user_input: str):
    # 1. The System Prompt (Persona + Strict JSON rules)
    system_prompt = """
    You are a Zero-Waste Culinary Assistant. Your goal is to suggest meals that prioritize using the user's expiring ingredients. 
    
    You MUST always reply in valid JSON format using exactly these keys: "recipe_name", "expiring_ingredients" (a list of strings), and "instructions". Do not include any conversational text before or after the JSON.
    """
    
    # 2. The Tool Instruction Manual
    agent_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_expiration_date",
                "description": "Calculates how many days until an ingredient expires.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ingredient": {
                            "type": "string",
                            "description": "The name of the ingredient (e.g., spinach, chicken)"
                        }
                    },
                    "required": ["ingredient"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    print("\n[Agent Thinking...]")
    
    # 3. First API Call (Agent decides if it needs a tool)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=agent_tools,
        temperature=0.3 
    )
    
    response_message = response.choices[0].message

    # 4. Check if the model decided to use a tool
    if response_message.tool_calls:
        # Append the model's tool request to our conversation history
        messages.append(response_message)
        
        # Loop through the requested tools
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            
            # Parse the arguments the LLM provided
            arguments = json.loads(tool_call.function.arguments)
            
            if function_name == "get_expiration_date":
                ingredient_name = arguments.get("ingredient")
                print(f"[Running Tool] Checking expiration for {ingredient_name}...")
                
                # Run the actual Python function
                tool_result = get_expiration_date(ingredient_name)
                
                # Add the function's output back to the conversation
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_result
                })
        
        # 5. Send the conversation back to the LLM with the new data
        print("[Agent Generating Final Recipe...]")
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3
        )
        return second_response.choices[0].message.content
        
    # If the model didn't need a tool, just return its normal text
    return response_message.content

if __name__ == "__main__":
    print("Welcome to the Culinary Agent. Type 'exit' to quit.")
    
    while True:
        user_query = input("\nWhat are we solving for today? > ")
        if user_query.lower() == 'exit':
            break
            
        answer = agent_loop(user_query)
        print(f"\n[Agent Action/Response]:\n{answer}")