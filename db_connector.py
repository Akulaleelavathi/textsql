from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URL
from langgraph.graph import StateGraph

# Define state for LangGraph
class SQLState:
    def __init__(self, query: str):
        self.query = query
        self.result = None
        self.error = None

def execute_query(state: SQLState):
    """Executes the SQL query and updates the state."""
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as connection:
            result = connection.execute(state.query)
            state.result = [row._asdict() for row in result]
    except SQLAlchemyError as e:
        state.error = str(e)
    return state

# Define the graph
graph = StateGraph(SQLState)

# Fix: Add missing identify_table node
def identify_table(state: SQLState):
    """Placeholder function to process or identify tables before execution."""
    return state

graph.add_node("identify_table", identify_table)  # Add this function
graph.add_node("execute_query", execute_query)
graph.add_edge("identify_table", "execute_query")  # Set the flow

graph.set_entry_point("identify_table")  # Keep as entry point

# Compile the graph (place this after defining nodes and edges)
workflow = graph.compile()

def run_sql_query(sql_query: str):
    state = SQLState(query=sql_query)
    final_state = workflow.run(state)
    if final_state.error:
        return {"error": final_state.error}
    return final_state.result
