import os
import openai
from openai import AzureOpenAI
from langgraph.graph import StateGraph
from pydantic import BaseModel
from typing import Dict

# Set up OpenAI API Key (Use environment variables for security)
os.environ["OPENAI_API_KEY"] = "3fa63f591fde45c6a32b9dc06e2af714"  # Replace with a secure method
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://contoso-chat-sf-ai-aiserviceskbxjjgy2qok56.openai.azure.com"

# Define Query Model
class QueryModel(BaseModel):
    user_question: str
    db_schema: dict
    table_name: str  # Add this field to store the table name


# Define SQL Query Generator Function
def generate_sql(state: QueryModel):
    """Generate SQL query using OpenAI"""
    user_question = state.user_question
    db_schema = state.db_schema
    table_name = state.table_name

    # Format schema as a readable text
    schema_text = "\n".join([f"{column}: {data_type}" for column, data_type in db_schema.items()])
    
    prompt = f"""
    You are an expert SQL query generator for Amazon Redshift.
    Below is the database schema for the table '{table_name}':
    {schema_text}

    Convert the following user question into a valid SQL query:
    User Question: {user_question}

    SQL Query:
    """

    
    client = AzureOpenAI(
    api_key="3fa63f591fde45c6a32b9dc06e2af714",
    api_version="2024-08-01-preview",
    azure_endpoint="https://contoso-chat-sf-ai-aiserviceskbxjjgy2qok56.openai.azure.com"
)

    # Ensure correct message formatting
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant specialized in SQL generation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    print("Raw Response from OpenAI:", response)  # Debugging

    # Extract SQL query safely
    try:
        sql_query = response.choices[0].message.content.strip()
    except (AttributeError, IndexError):
        sql_query = "ERROR: Unable to extract SQL query from response."

    print(f"Generated SQL Query: {sql_query}")  # Debugging
    return sql_query