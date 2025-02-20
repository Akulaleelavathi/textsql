# from sqlvalidator import SQLQuery

# def validate_sql(query: str) -> bool:
#     sql = SQLQuery(query)
#     return sql.is_valid()




from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI
from pydantic_ai import BaseAIModel  # Pydantic.AI for structured validation
from typing import Optional
from config import OPENAI_API_KEY  # Assuming API key is stored in a config file

# Initialize OpenAI LLM
llm = OpenAI(api_key=OPENAI_API_KEY, model="")

# Define Pydantic Model for SQL Query Validation
class SQLValidationInput(BaseAIModel):
    """Pydantic.AI model for validating SQL input."""
    query: str

class SQLValidationOutput(BaseAIModel):
    """Pydantic.AI model for structured SQL validation response."""
    is_valid: bool
    validated_query: Optional[str] = None
    error_message: Optional[str] = None

# Define the system prompt for SQL validation
system_prompt = """Double check the following Amazon Redshift SQL query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Checking that table and column names exist in the schema
- Ensuring Redshift-specific syntax (e.g., DISTKEY, SORTKEY) is correct

If there are any mistakes, return 'INVALID' along with a brief reason.
If the query is correct, return 'VALID'.

Output format:
{"is_valid": true/false, "validated_query": "query or None", "error_message": "error reason or None"}
"""

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{query}")
])

# Function to validate SQL query with retry logic
def validate_sql(query: str, max_retries=3) -> SQLValidationOutput:
    """Validates an SQL query using LLM and retries if invalid."""
    validation_chain = prompt | llm | StrOutputParser()
    retries = 0

    while retries < max_retries:
        validation_result = validation_chain.invoke({"query": query}).strip()

        try:
            # Parse result into Pydantic model
            parsed_result = SQLValidationOutput.model_validate_json(validation_result)

            if parsed_result.is_valid:
                return parsed_result  # Return valid query response
            else:
                print(f"Retry {retries + 1}: Invalid query detected. Retrying...")
                query = fix_query_with_llm(query)  # Ask LLM to fix query automatically
                retries += 1
        except Exception as e:
            return SQLValidationOutput(is_valid=False, error_message=f"Parsing Error: {str(e)}")

    return SQLValidationOutput(is_valid=False, error_message="Query validation failed after 3 retries.")

# Function to ask LLM to fix the SQL query
def fix_query_with_llm(query: str) -> str:
    """Asks LLM to fix an invalid query."""
    fix_prompt = ChatPromptTemplate.from_messages([
        ("system", "Fix the following Redshift SQL query and return the corrected query ONLY."),
        ("human", "{query}")
    ])
    fix_chain = fix_prompt | llm | StrOutputParser()
    return fix_chain.invoke({"query": query}).strip()
