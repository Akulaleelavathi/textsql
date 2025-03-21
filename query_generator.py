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
    db_schema: Dict[str, list]  # Renamed from `schema` to `db_schema`

# Define SQL Query Generator Function
def generate_sql(state: QueryModel):
    """Generate SQL query using OpenAI"""
    user_question = state.user_question
    db_schema = state.db_schema

    schema_text = "\n".join([f"{table}: {', '.join(fields)}" for table, fields in db_schema.items()])
    prompt = f"""
    You are an expert SQL query generator for Amazon Redshift.
    Below is the database schema:
    {schema_text}

    Convert the following user question into a valid SQL query using the correct table and field names:
    User Question: {user_question}
    SQL Query:
    """

    client = AzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  
        api_version="2024-08-01-preview",
        azure_endpoint="https://contoso-chat-sf-ai-aiserviceskbxjjgy2qok56.openai.azure.com"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.5
    )

    # DEBUG: Print the response to check its structure
    print("Raw Response from OpenAI:", response)

    # Ensure response contains valid data before accessing keys
    if hasattr(response, "choices") and response.choices:
        first_choice = response.choices[0]
        if hasattr(first_choice, "message") and hasattr(first_choice.message, "content"):
            sql_query = first_choice.message.content.strip()
        else:
            sql_query = "ERROR: Response message content not found"
    else:
        sql_query = "ERROR: No valid response received"

    return {"sql_query": sql_query}

# Create LangGraph Workflow
workflow = StateGraph(QueryModel)

# Add Nodes
workflow.add_node("generate_sql", generate_sql)

# Define Start & End
workflow.set_entry_point("generate_sql")
workflow.set_finish_point("generate_sql")

# Compile Graph
graph = workflow.compile()

