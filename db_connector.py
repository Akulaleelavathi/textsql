from sqlalchemy import create_engine, text
# from config import DATABASE_URL
from urllib.parse import quote_plus
password = "Service@007"
encoded_password = quote_plus(password)
DATABASE_URL = f"postgresql+psycopg2://zonoservice:{encoded_password}@localhost:5440/qa"

def execute_query(sql_query: str):
    print("sql query---------------->",sql_query)
    """Executes the given SQL query and returns the result."""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            return [dict(row) for row in result]
    except Exception as e: 
        return {"error": str(e)}
