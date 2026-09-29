import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def agent_loop(user_input: str):
    # 1. The updated System Prompt enforcing JSON
    system_prompt = """
    You are a Zero-Waste Culinary Assistant. Your goal is to suggest meals that prioritize using the user's expiring ingredients. 
    
    You MUST always reply in valid JSON format using exactly these keys: "recipe_name", "expiring_ingredients" (a list of strings), and "instructions". 
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    print(f"\n[Agent Thinking...]")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={ "type": "json_object" },
        temperature=0.3 
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Welcome to the Culinary Agent. Type 'exit' to quit.")
    
    while True:
        user_query = input("\nWhat are we solving for today? > ")
        if user_query.lower() == 'exit':
            break
            
        answer = agent_loop(user_query)
        print(f"\n[Agent Action/Response]:\n{answer}")