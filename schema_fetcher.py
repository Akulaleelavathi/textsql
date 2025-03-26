from sqlalchemy import create_engine, inspect, text
from config import DATABASE_URL
 
def fetch_redshift_schema(schema_name="reports", table_name=None):
    """Fetch schema details for a specific table or all tables in the given Redshift schema."""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    schema_output = ""
 
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = :schema"),
                {"schema": schema_name}
            )
            table_names = [row[0] for row in result]
 
        if table_name:
            if table_name not in table_names:
                return f"Table '{table_name}' not found in schema '{schema_name}'."
            table_names = [table_name]
 
        if not table_names:
            return f"No tables found in schema '{schema_name}'."
 
        for table in table_names:
            schema_output += f"Table: {table}\n"
 
            # Fetch column details
            columns = inspector.get_columns(table, schema=schema_name)
            for column in columns:
                col_name = column["name"]
                col_type = str(column["type"])
                constraints = []
 
                if column.get("primary_key"):
                    constraints.append("Primary Key")
 
                if column.get("foreign_keys"):
                    for fk in column["foreign_keys"]:
                        constraints.append(f"Foreign Key to {fk['referred_table']}.{fk['referred_column']}")
 
                constraint_str = f" ({', '.join(constraints)})" if constraints else ""
                schema_output += f"- {col_name}: {col_type}{constraint_str}\n"
 
            schema_output += "\n"  # Blank line between tables
 
        print("\n=== Final Extracted Schema ===\n", schema_output.strip())  # Print final schema
        return schema_output.strip()
 
    except Exception as e:
        print(f"Error fetching schema: {e}")
        return f"Error fetching schema: {e}"
 
    finally:
        engine.dispose()  # Properly close the engine
 

 