import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def agent_loop(user_input: str):
    
    system_prompt = """
    You are an intelligent culinary agent. Your goal is to solve meal constraints 
    based on the user's available ingredients, time, and physical context.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    print(f"\n[Agent Thinking...]")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
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