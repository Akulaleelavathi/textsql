from sqlalchemy import create_engine, inspect
from config import DATABASE_URL

def fetch_redshift_schema(schema_name="reports", table_name=None):
    """Fetch schema details for a specific table or all tables in the given Redshift schema."""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    schema_lines = []

    try:
        # Fetch table names from Redshift system catalog instead of relying on SQLAlchemy's inspector
        with engine.connect() as conn:
            result = conn.execute(
                f"SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = '{schema_name}'"
            )
            table_names = [row[0] for row in result]

        if table_name:  # If a specific table is requested, filter the list
            table_names = [table_name] if table_name in table_names else []

        for table in table_names:
            schema_lines.append(f"Table: {table}")

            for column in inspector.get_columns(table, schema=schema_name):
                col_name = column["name"]
                col_type = str(column["type"])

                if column.get("primary_key"):
                    col_type += ", Primary Key"

                if column.get("foreign_keys"):
                    for fk in column["foreign_keys"]:
                        col_type += f", Foreign Key to {fk['referred_table']}.{fk['referred_column']}"

                schema_lines.append(f"- {col_name}: {col_type}")

            schema_lines.append("")  # Blank line between tables

        # Print the schema after fetching
        print("Retrieved database schema.----------->", "\n".join(schema_lines))
        return "\n".join(schema_lines)

    except Exception as e:
        print(f"Error fetching schema: {e}")
        return f"Error fetching schema: {e}"

# Call the function and print the schema
fetch_redshift_schema()  # This will print the schema for the 'reports' schema by default
