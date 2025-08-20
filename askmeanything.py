import wikipedia
from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

#Load environment variable from .env file
load_dotenv()
api_key = os.getenv("AZURE_OPENAI_API_KEYAZURE_OPENAI_ENDPOINT")

#Tool 1: calculator
def calculator_tool(expression:str)-> str:
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"
    

#Tool 2: Wikipedia Search
def wiki_tool(query:str)-> str:
    try:
        return wikipedia.summary(query,sentences = 2)
    except Exception as e:
        return f"Error: {e}"
    

#Defining Agent
client = OpenAI(api_key = api_key)
def agent(user_input):   #Ask LLM if it needs math, wiki or direct answer?
    prompt = f""" You are an AI agent. Decide if the user query needs :
                    1. Calculator
                    2. Wikipedia
                    3. AI generated
                    If Calculator is needed, extract only the pure math expression (no text). 
                    Return only the expression in ASCII. No LaTeX or words
                    Example:
                    User: "What is 10 -8?" -> calculate 10-8
                Query : {user_input}
                Answer only with 'calculator', 'wikipedia' or 'AI generated'."""
    decision = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{"role":"user","content":prompt}])
    
    tool_choice = decision.choices[0].message.content.strip().lower()
    print(f"Agent Decision: ",tool_choice)
    #call tool if needed
    if tool_choice.startswith("calculator"):
        response = client.chat.completions.create(model= "gpt-4o-mini",messages = [{"role":"user",
                     "content": f"Extract the pure math expression from: {user_input}."
                     "Return only the expression in ASCII. No LaTeX or words"}])
        expression = response.choices[0].message.content.strip()
        return "Answer:" + calculator_tool(expression)
    
    elif "wikipedia" in tool_choice:
        return "Answer:" + wiki_tool(user_input)
    
    else:
        response = client.chat.completions.create(               #LLM replies 
            model = "gpt-4o-mini",
            messages= [{"role":"user","content": user_input}]
        )

    return response.choices[0].message.content

#Testing
# print(agent("Calculate 25+5"))
# print(agent("Who is Albert Einstein"))
# print(agent("Tell a motivational quote"))


#Title of the app
st.title("Ask Me Anything")

st.subheader("What would you like to find out?")
user_question = st.text_input("Enter your question")
if user_question:
    with st.spinner("Generating response..."):
        reply = agent(user_question)
        st.markdown("### Response")
        st.write(reply)

# else:

#     st.info("I don't understand your question, please try again")

