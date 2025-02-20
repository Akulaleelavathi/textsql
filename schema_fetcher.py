from sqlalchemy import create_engine
import pandas as pd
from config import DATABASE_URL

def fetch_redshift_schema():
    """Fetch schema details (tables and columns) from Redshift."""
    engine = create_engine(DATABASE_URL)
    query = """
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public';
    """
    
    with engine.connect() as connection:
        result = connection.execute(query)
        schema_df = pd.DataFrame(result.fetchall(), columns=['table_name', 'column_name', 'data_type'])

    # Convert schema into a dictionary
    schema_dict = {}
    for _, row in schema_df.iterrows():
        table = row["table_name"]
        column = row["column_name"]
        datatype = row["data_type"]

        if table not in schema_dict:
            schema_dict[table] = []
        schema_dict[table].append((column, datatype))

    return schema_dict
