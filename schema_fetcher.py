from sqlalchemy import create_engine
import pandas as pd
from config import DATABASE_URL

def fetch_redshift_schema(table_name):
    """Fetch schema details (columns and data types) for a specific table from Redshift."""
    engine = create_engine(DATABASE_URL)
    query = f"""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = '{table_name}';
    """
    
    with engine.connect() as connection:
        result = connection.execute(query)
        schema_df = pd.DataFrame(result.fetchall(), columns=['table_name', 'column_name', 'data_type'])

    # If table schema is not found
    if schema_df.empty:
        return f"No schema found for table '{table_name}'."

    # Convert schema into a dictionary
    schema_dict = {table_name: []}
    for _, row in schema_df.iterrows():
        column = row["column_name"]
        datatype = row["data_type"]
        schema_dict[table_name].append((column, datatype))

    return schema_dict

# Example usage
table = "your_table_name"  # Replace with actual table name from the prompt
schema = fetch_redshift_schema(table)
print(schema)
