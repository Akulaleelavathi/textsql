from pydantic_ai import OpenAIModel
from config import OPENAI_API_KEY

class QueryModel(OpenAIModel):
    user_question: str
    schema: dict  # Pass database schema
    sql_query: str

    class Config:
        openai_model = ""
        prompt_template = """
        You are an expert SQL query generator for Amazon Redshift.
        Below is the database schema:
        {schema}

        Convert the following user question into a valid SQL query using the correct table and field names:
        User Question: {user_question}
        SQL Query:
        """
