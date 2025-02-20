from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URL

def execute_query(sql_query: str):
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as connection:
            result = connection.execute(sql_query)
            return [row._asdict() for row in result]  # Convert result to a list of dictionaries
    except SQLAlchemyError as e:
        return {"error": str(e)}
