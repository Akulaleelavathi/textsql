from typing import Optional
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI
from pydantic import BaseModel
import json
from openai import AzureOpenAI

# Initialize OpenAI LLM
client = AzureOpenAI(
    api_key="3fa63f591fde45c6a32b9dc06e2af714",
    api_version="2024-08-01-preview",
    azure_endpoint="https://contoso-chat-sf-ai-aiserviceskbxjjgy2qok56.openai.azure.com"
)

# Define Pydantic Model for SQL Query Validation
class SQLValidationInput(BaseModel):
    """Pydantic model for validating SQL input."""
    query: str

class SQLValidationOutput(BaseModel):
    """Pydantic model for structured SQL validation response."""
    is_valid: bool
    validated_query: Optional[str] = None
    error_message: Optional[str] = None

# Define the system prompt for SQL validation
system_prompt = """You are an expert in Amazon Redshift SQL validation. Your job is to check the given SQL query for common mistakes and provide a structured response.

### Validation Criteria:
1. **Syntax and Formatting:**
   - Ensure correct Redshift-specific syntax (e.g., DISTKEY, SORTKEY, COPY commands).
   - Properly quote identifiers and avoid unnecessary quotation marks.
2. **Logical Issues:**
   - Using `NOT IN` with NULL values can lead to incorrect results.
   - `UNION` vs. `UNION ALL` - Use `UNION ALL` if duplicates are allowed.
   - `BETWEEN` includes both endpoints. Ensure exclusive range if needed.
3. **Data Type Consistency:**
   - Ensure correct number and type of arguments for functions.
   - Verify explicit casting where necessary.
4. **Schema Validation:**
   - Ensure referenced table and column names exist.
   - Validate primary and foreign key constraints.
5. **Performance Optimization:**
   - Ensure proper indexes and sorting keys are used.
   - Avoid SELECT * in large tables for efficiency.

### Output Format:
Respond in JSON format:
```json
{
    "is_valid": true/false,
    "validated_query": "corrected SQL query or None",
    "error_message": "Explanation of issue or None"
}
```
"""

# Create a prompt template
validation_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Query: {query}")
])

# Function to validate SQL query with retry logic
def validate_sql(query: str, max_retries=3) -> SQLValidationOutput:
    """Validates an SQL query using LLM and retries if invalid."""
    validation_chain = validation_prompt | StrOutputParser()
    retries = 0

    while retries < max_retries:
        # Send request to LLM
        response = client.invoke(validation_chain.format(query=query)).strip()

        try:
            # Parse response
            parsed_result = SQLValidationOutput.model_validate(json.loads(response))

            if parsed_result.is_valid:
                return parsed_result  # Return valid query response
            else:
                print(f"Retry {retries + 1}: Invalid query detected. Retrying...")
                query = fix_query_with_llm(query, parsed_result.error_message)  # Fix query automatically
                retries += 1
        except Exception as e:
            return SQLValidationOutput(is_valid=False, error_message=f"Parsing Error: {str(e)}")

    return SQLValidationOutput(is_valid=False, error_message="Query validation failed after 3 retries.")

# Function to ask LLM to fix the SQL query
def fix_query_with_llm(query: str, error_message: str) -> str:
    """Asks LLM to fix an invalid query based on the detected issue."""
    fix_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert in Amazon Redshift SQL optimization and correction. Given an incorrect SQL query and its issue, return a corrected version of the query."),
        ("human", "Query: {query}\nError: {error_message}")
    ])
    fix_chain = fix_prompt | StrOutputParser()

    return client.invoke(fix_chain.format(query=query, error_message=error_message)).strip()

# # Example Usage
# if __name__ == "__main__":
#     test_query = "SELECT * FROM orders WHERE order_date BETWEEN '2023-01-01' AND '2023-12-31';"
#     result = validate_sql(test_query)
#     print(result)
