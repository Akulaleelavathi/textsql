from pydantic import BaseModel
from schema_fetcher import fetch_redshift_schema
from query_generator import QueryModel
from sql_validator import validate_sql
from db_connector import execute_query

class UserQuery(BaseModel):
    user_question: str

def process_user_query(user_input: UserQuery):
    """Processes a user question by generating, validating, and executing SQL."""
    schema_dict = fetch_redshift_schema()

    query_instance = QueryModel(user_question=user_input.user_question, schema=schema_dict)
    generated_sql = query_instance.sql_query

    validation_result = validate_sql(generated_sql)

    if not validation_result.is_valid:
        return {"error": validation_result.error_message}

    response = execute_query(validation_result.validated_query)
    return response

if __name__ == "__main__":
    user_input = input("Enter your question: ")
    user_query = UserQuery(user_question=user_input)  # Validate input using Pydantic
    response = process_user_query(user_query)
    print(response)
