import streamlit as st
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

# Define graph state
class QueryState(BaseModel):
    user_input: UserQuery
    table_name: str = ""
    schema_dict: dict = {}
    generated_sql: str = ""
    validation_result: dict = {}
    response: dict = {}

# Define nodes
def identify_table_node(state: QueryState) -> QueryState:
    state.table_name = identify_tables(state.user_input.user_question)
    print(f"identify_table_node -> Identified table: {state.table_name}")
    return state




# def fetch_schema_node(state: QueryState) -> QueryState:
#     state.schema_dict = fetch_redshift_schema(state.table_name)
    
#     if isinstance(state.schema_dict, str):
#         state.response = {"error": state.schema_dict}
#         print(f"Error found, setting response: {state.response}")  # Debug print for error case
#         return state  # Return the modified state directly
    
#     print(f"fetch_schema_node -> Returning state with schema_dict: {state.schema_dict}")
#     return state


def fetch_schema_node(state: QueryState) -> QueryState:
    state.schema_dict = fetch_redshift_schema("zoai_invoice_report")
    
    if isinstance(state.schema_dict, str):
        state.response = {"error": state.schema_dict}
        print(f"Error found, setting response: {state.response}")  # Debug print for error case
        return state  # Return the modified state directly
    
    print(f"fetch_schema_node -> Returning state with schema_dict: {state.schema_dict}")
    return state



def generate_query_node(state: QueryState) -> QueryState:
    example_query = EXAMPLE_QUERIES.get(state.table_name, "")
    query_instance = QueryModel(
        user_question=state.user_input.user_question,
        schema=state.schema_dict,
        example_query=example_query
    )
    state.generated_sql = query_instance.sql_query
    print(f"generate_query_node -> Generated SQL: {state.generated_sql}")
    return state

def validate_sql_node(state: QueryState) -> QueryState:
    validation = validate_sql(state.generated_sql)
    print(f"validate_sql_node -> Validation result: {validation.is_valid}")
    if not validation.is_valid:
        return QueryState(**state.dict(), response={"error": validation.error_message})
    state.validation_result = validation.validated_query
    return state

def execute_query_node(state: QueryState) -> QueryState:
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
    if st.button("Submit"):
        if user_input.strip():
            user_query = UserQuery(user_question=user_input)
            initial_state = QueryState(user_input=user_query)
            print(f"Initial state: {initial_state}")
            final_state = workflow.invoke(initial_state)
            print(f"Final state: {final_state}")
            st.json(final_state.response)
        else:
            st.warning("Please enter a valid question.")

if __name__ == "__main__":
    main()
