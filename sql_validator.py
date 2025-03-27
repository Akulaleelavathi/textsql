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
class SQLValidationOutput(BaseModel):
    is_valid: bool
    error_message: Optional[str] = ""

# Define the system prompt for SQL validation
system_prompt = """You are an expert in Amazon Redshift SQL validation. Your job is to check the given SQL query for syntax and logical errors.

### Validation Criteria:
1. **Syntax and Formatting:** Ensure correct Redshift-specific syntax.
2. **Logical Issues:** Detect NULL handling issues, `UNION` misuse, etc.
3. **Data Type Consistency:** Ensure function arguments and casting are correct.
4. **Schema Validation:** Verify table and column existence.
5. **Performance Optimization:** Check indexing and avoid `SELECT *` for large tables.

### Output Format:
Respond in JSON format:
```json
{
    "is_valid": true/false,
    "error_message": "Explanation of issue or None"
}
```
"""

# Create a prompt template
validation_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Query: {query}")
])

# Function to validate SQL query
def validate_sql(query: str) -> SQLValidationOutput:
    """Validates an SQL query using LLM."""
    validation_chain = validation_prompt | StrOutputParser()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": validation_chain.invoke({"query": query})}]
        ).choices[0].message.content.strip()
        
        parsed_result = SQLValidationOutput.model_validate(json.loads(response))
        return parsed_result
    
    except json.JSONDecodeError:
        return SQLValidationOutput(is_valid=False, error_message="Error parsing LLM response. Invalid JSON format.")
    except Exception as e:
        return SQLValidationOutput(is_valid=False, error_message=f"Unexpected Error: {str(e)}")

# Example Usage
# if __name__ == "__main__":
#     user_query = input("Enter your SQL query: ")
#     result = validate_sql(user_query)
#     print(f"Valid: {result.is_valid}, Error: {result.error_message}")
