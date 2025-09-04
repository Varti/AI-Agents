import streamlit as st
import pandas as pd
from openai import AzureOpenAI
import os
from dotenv import load_dotenv


load_dotenv()  # Load variables from .env


# Set your OpenAI API key

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
# model_name = os.getenv("model_name")
# deployment = os.getenv("deployment")

subscription_key =os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# Title of the app
st.title("Data Exploration and Insights Agent")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# Load data
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file, engine='openpyxl')

# Dataset summary
def summarize_dataset(df):
    st.subheader("Dataset Summary")
    st.write("**Shape:**", df.shape)
    st.write("**Columns and Data Types:**")
    st.write(df.dtypes)
    st.write("**Missing Values:**")
    st.write(df.isnull().sum())

# Descriptive statistics
def show_statistics(df):
    st.subheader("Descriptive Statistics")
    st.write(df.describe(include='all'))

# GPT-4 insights
def generate_insights(df, question):
    prompt = f"""
    You are a data analyst. Based on the following dataset summary and statistics, answer the question below:\n\n
    Dataset Columns: {df.columns.tolist()}\n
    First few rows:\n{df.head().to_string()}\n\n
    Question: {question}\n
    Analyze the data, share the observations in a concise and insightful manner.
    """
    # client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    insight = response.choices[0].message.content

    return response['choices'][0]['message']['content']

# Main logic
if uploaded_file:
    df = load_data(uploaded_file)
    summarize_dataset(df)
    show_statistics(df)

    st.subheader("Ask a Question About the Data")
    user_question = st.text_input("Enter your question (e.g., What are the top 5 products by sales?)")

    if user_question:
        with st.spinner("Generating insight..."):
            insight = generate_insights(df, user_question)
            st.markdown("### Insight")
            st.write(insight)
else:
    st.info("Please upload a CSV or Excel file to begin.")


