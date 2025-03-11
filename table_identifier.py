def identify_tables(user_question: str) -> list:
    """
    Extracts table names from the user question using simple keyword matching.
    Returns a list of table names that are present in the question.
    
    For a production scenario, you might use NLP techniques to improve accuracy.
    """
    lowered = user_question.lower()
    tables = []
    
    if "orders" in lowered:
        tables.append("orders")
    if "invoice" in lowered:
        tables.append("invoice")
    if "payment" in lowered:
        tables.append("payment")
    if "dispatch" in lowered:
        tables.append("dispatch")
    
    # If no recognized table is found, return a default value.
    if not tables:
        tables.append("default_table")
    
    return tables

# # Example usage
# if __name__ == "__main__":
#     user_question = input("Enter your question: ")
#     result = identify_tables(user_question)
#     print("Identified tables:", result)

