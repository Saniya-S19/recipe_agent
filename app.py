import streamlit as st
import json
from main import agent_loop

st.set_page_config(page_title="Culinary Agent", page_icon="🍳")

st.title("🍳 Zero-Waste Culinary Agent")
st.markdown("Enter your ingredients below, and the agent will use its tools to build a context-aware recipe.")

# Streamlit chat interface
user_query = st.chat_input("What are we solving for today?")

if user_query:
    # Display user message
    with st.chat_message("user"):
        st.write(user_query)
        
    # Display agent response
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking and using tools..."):
            answer = agent_loop(user_query)
            
            # Use your existing UI parser logic for a clean display
            try:
                clean_answer = answer.replace('```json', '').replace('```', '').strip()
                recipe_data = json.loads(clean_answer)
                
                st.subheader(f"🍽️ {recipe_data.get('recipe_name', 'Chef Special')}")
                st.caption(f"🕒 MEAL TYPE: {recipe_data.get('meal_type', 'Any')}")
                st.error(f"⚠️ EXPIRING: {', '.join(recipe_data.get('expiring_ingredients', []))}")
                st.info(f"💪 NUTRITION: {recipe_data.get('nutrition_notes', 'N/A')}")
                st.write(f"**Instructions:**\n{recipe_data.get('instructions', 'N/A')}")
                
            except json.JSONDecodeError:
                st.write(answer)