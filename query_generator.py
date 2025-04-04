import os
import re
from openai import AzureOpenAI
from pydantic import BaseModel
from typing import Dict

# Set up OpenAI API Key (Use environment variables for security)
os.environ["OPENAI_API_KEY"] = "3fa63f591fde45c6a32b9dc06e2af714"  # Replace with a secure method
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://contoso-chat-sf-ai-aiserviceskbxjjgy2qok56.openai.azure.com"

# Define Query Model
class QueryModel(BaseModel):
    user_question: str
    db_schema: Dict[str, str]
    table_name: str  # Store the table name

# Define the core SQL generation logic
def actual_logic_to_generate_sql(query_instance: QueryModel) -> str:
    """Generate SQL query using OpenAI"""
    user_question = query_instance.user_question
    db_schema = query_instance.db_schema
    table_name = query_instance.table_name

    # Format schema as readable text
    schema_text = "\n".join([f"{column}: {data_type}" for column, data_type in db_schema.items()])

    prompt = f"""
    You are an expert SQL query generator for Amazon Redshift.
    Below is the database schema for the table 'reports.{table_name}':
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
        return response.choices[0].message.content.strip()
    except (AttributeError, IndexError):
        return "ERROR: Unable to extract SQL query from response."

# Wrapper function to clean up SQL output
def generate_sql(query_instance: QueryModel) -> str:
    """
    Generate a valid SQL query without extra text.
    """
    sql_query = actual_logic_to_generate_sql(query_instance)  # Generate SQL query

    # Ensure only the SQL query is returned
    sql_query = sql_query.strip()

    if sql_query.startswith("To retrieve") or "```sql" in sql_query:
        # Extract SQL from explanation
        match = re.search(r"```sql\n(.*?)\n```", sql_query, re.DOTALL)
        if match:
            sql_query = match.group(1).strip()

    print(f"✅ Final Cleaned SQL: {sql_query}")  # Debugging

    return sql_query
