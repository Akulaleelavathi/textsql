from pydantic import BaseModel
from schema_fetcher import fetch_redshift_schema  # This now accepts a table name.
from query_generator import QueryModel
from sql_validator import validate_sql
from db_connector import execute_query
from table_identifier import identify_tables # Import the identify_table function.
from example_queries import EXAMPLE_QUERIES  # Import the example queries dictionary.

class UserQuery(BaseModel):
    user_question: str

def process_user_query(user_input: UserQuery):
    """Processes a user question by determining the table, fetching its schema, generating, validating, and executing SQL."""
    # Identify the table based on the user question.
    table_name = identify_tables(user_input.user_question)
    print(f"Identified table: {table_name}")

    # Fetch the schema for the identified table.
    schema_dict = fetch_redshift_schema(table_name)
    if isinstance(schema_dict, str):  # Check if an error message was returned.
        return {"error": schema_dict}

    # Retrieve an example query if available.
    table_name_queries= EXAMPLE_QUERIES.get(table_name, "")

    # Generate the SQL query using the QueryModel.
    query_instance = QueryModel(
        user_question=user_input.user_question,
        schema=schema_dict,
        example_query=table_name_queries  # Assuming QueryModel accepts an example_query parameter.
    )
    generated_sql = query_instance.sql_query

    # Validate the generated SQL.
    validation_result = validate_sql(generated_sql)
    if not validation_result.is_valid:
        return {"error": validation_result.error_message}

    # Execute the validated SQL query.
    response = execute_query(validation_result.validated_query)
    return response

if __name__ == "__main__":
    user_input = input("Enter your question: ")
    user_query = UserQuery(user_question=user_input)  # Validate input using Pydantic.
    response = process_user_query(user_query)
    print(response)
