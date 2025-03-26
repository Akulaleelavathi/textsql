import streamlit as st
import json
import re

from pydantic import BaseModel
from openai import OpenAI  # Use OpenAI's package instead
from langgraph.graph import StateGraph
from schema_fetcher import fetch_redshift_schema
from query_generator import QueryModel
from sql_validator import validate_sql
from db_connector import execute_query
from table_identifier import identify_tables
from example_queries import EXAMPLE_QUERIES

# Define input model
class UserQuery(BaseModel):
    user_question: str
    table_name: str = ""  # Allows manual table name input

# Define graph state
class QueryState(BaseModel):
    user_input: UserQuery
    table_name: str = ""
    schema_dict: dict = {}  # Ensure it's always a dictionary
    generated_sql: str = ""
    validation_result: str = ""  # Store the validated SQL query as a string
    response: dict = {}


# Define nodes
def identify_table_node(state: QueryState) -> QueryState:
    if state.user_input.table_name:  # Use manually provided table name
        state.table_name = state.user_input.table_name
        print(f"identify_table_node -> Using manually entered table name: {state.table_name}")
    else:
        state.table_name = identify_tables(state.user_input.user_question)  # Auto-detect if not provided
        print(f"identify_table_node -> Identified table: {state.table_name}")
    return state





def parse_schema(schema_str):
    """
    Parses a formatted schema string and converts it into a dictionary.
    """
    schema_dict = {}
    lines = schema_str.strip().split("\n")

    for line in lines:
        match = re.match(r"- (\w+): (\w+\(?\d*\)?)", line.strip())
        if match:
            column_name, column_type = match.groups()
            schema_dict[column_name] = column_type

    return schema_dict

def fetch_schema_node(state: QueryState) -> QueryState:
    if not state.table_name:
        state.response = {"error": "Table name is missing."}
        return state

    schema = fetch_redshift_schema(table_name=state.table_name)  # Fetch schema

    print(f"fetch_schema_node -> Raw Schema received: {schema} (Type: {type(schema)})")  # Debugging

    # If schema is a formatted string, parse it
    if isinstance(schema, str):
        state.schema_dict = parse_schema(schema)
    elif isinstance(schema, dict):
        state.schema_dict = schema
    else:
        state.schema_dict = {}

    if state.schema_dict:
        print(f"fetch_schema_node -> Parsed schema_dict: {state.schema_dict}")
    else:
        state.response = {"error": "Failed to parse schema."}
        print("fetch_schema_node -> Error: Schema not parsed correctly.")

    return state






def generate_query_node(state: QueryState) -> QueryState:
    print(f"generate_query_node -> Received schema_dict: {state.schema_dict}")  # Debugging print

    if not state.schema_dict:
        state.response = {"error": "Schema not found. Ensure table name is correct and schema is accessible."}
        print("generate_query_node -> Schema Dict Empty. Check fetch_schema_node.")
        return state

    example_query = EXAMPLE_QUERIES.get(state.table_name, None)
    if not example_query:
        print(f"generate_query_node -> Warning: No example query found for table {state.table_name}")
        example_query = ""  # Fallback to an empty query

    try:
        query_instance = QueryModel(
            user_question=state.user_input.user_question,
            db_schema=state.schema_dict,
            example_query=example_query
        )
        state.generated_sql = query_instance.generate_sql()  # Ensure SQL is generated
        print(f"generate_query_node -> Generated SQL: {state.generated_sql}")
    except Exception as e:
        print(f"generate_query_node -> Error in Query Generation: {str(e)}")
        state.response = {"error": f"SQL Generation failed: {str(e)}"}
        return state

    return state



def validate_sql_node(state: QueryState) -> QueryState:
    validation = validate_sql(state.generated_sql)
    print(f"validate_sql_node -> Validation result: {validation.is_valid}")
    
    if not state.generated_sql.strip():
        state.response = {"error": "SQL query generation failed."}
        return state

    
    # Ensure validation_result contains a valid SQL query
    state.validation_result = validation.validated_query.get("query", "") if isinstance(validation.validated_query, dict) else validation.validated_query
    return state


def execute_query_node(state: QueryState) -> QueryState:
    if not isinstance(state.validation_result, str) or not state.validation_result.strip():
        state.response = {"error": "Invalid SQL query for execution."}
        return state

    state.response = execute_query(state.validation_result)
    print(f"execute_query_node -> Query execution response: {state.response}")
    return state


# Build LangGraph workflow
graph = StateGraph(QueryState)
graph.add_node("identify_table", identify_table_node)
graph.add_node("fetch_schema", fetch_schema_node)
graph.add_node("generate_query", generate_query_node)
graph.add_node("validate_sql", validate_sql_node)
graph.add_node("execute_query", execute_query_node)

graph.add_edge("identify_table", "fetch_schema")
graph.add_edge("fetch_schema", "generate_query")
graph.add_edge("generate_query", "validate_sql")
graph.add_edge("validate_sql", "execute_query")

# Set the entry point
graph.set_entry_point("identify_table")

# Mark execute_query as the end node
graph.set_finish_point("execute_query")

# Compile graph
workflow = graph.compile()

# Streamlit UI
def main():
    st.title("SQL Query Generator and Executor with LangGraph")
    st.write("Enter your question and get an SQL query generated, validated, and executed!")

    user_input = st.text_area("Enter your question:")
    table_name = st.text_input("Enter table name (leave blank for auto-detect):")

    if st.button("Submit"):
        if user_input.strip():
            user_query = UserQuery(user_question=user_input, table_name=table_name.strip())
            initial_state = QueryState(user_input=user_query)
            print(f"Initial state: {initial_state}")
            final_state = QueryState(**workflow.invoke(initial_state))

            
            # Ensure final_state is an object and extract response safely
            if final_state.response.get("error"):
                st.error(final_state.response["error"])
            else:
                st.subheader("Generated SQL Query:")
                st.code(final_state.generated_sql or "No SQL generated", language="sql")
                
                st.subheader("Query Execution Result:")
                st.json(final_state.response or {})

        else:
            st.warning("Please enter a valid question.")

if __name__ == "__main__":
    main()
