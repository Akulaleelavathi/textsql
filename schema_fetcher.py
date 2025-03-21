from sqlalchemy import create_engine, inspect
import pandas as pd
from config import DATABASE_URL
from main import QueryState

def fetch_redshift_schema(table_name=None):
    """Fetch schema details for a specific table or all tables in Redshift."""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        schema = ""

        with engine.connect() as connection:
            table_names = [table_name] if table_name else inspector.get_table_names(schema='public')
            if not table_names:
                return "Error: No tables found in the database."
            
            for table in table_names:
                schema += f"Table: {table}\n"
                for column in inspector.get_columns(table, schema='public'):
                    col_name = column["name"]
                    col_type = str(column["type"])

                    if column.get("primary_key"):
                        col_type += ", Primary Key"
                    if column.get("foreign_keys"):
                        fk_list = list(column["foreign_keys"])
                        if fk_list:
                            fk = fk_list[0]
                            col_type += f", Foreign Key to {fk.column.table.name}.{fk.column.name}"

                    schema += f"- {col_name}: {col_type}\n"
                
                schema += "\n"
        
        print("Retrieved database schema.")
        return schema
    
    except Exception as e:
        return f"Error fetching schema: {str(e)}"


def fetch_schema_node(state):
    try:
        if not state.table_name:
            raise ValueError("Table name could not be identified from user input.")
        
        state.schema_dict = fetch_redshift_schema(state.table_name)
        print(f"fetch_schema_node -> Fetched schema: {state.schema_dict}")
        
        if isinstance(state.schema_dict, str) and state.schema_dict.startswith("Error"):
            state.response = {"error": state.schema_dict}
            return state
        
        return state
    except Exception as e:
        return QueryState(**state.dict(), response={"error": str(e)})
