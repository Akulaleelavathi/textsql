from openai import AzureOpenAI


client = AzureOpenAI(
    api_key="3fa63f591fde45c6a32b9dc06e2af714",
    api_version="2024-08-01-preview", 
    azure_endpoint="https://contoso-chat-sf-ai-aiserviceskbxjjgy2qok56.openai.azure.com"
)

def identify_tables(user_question: str) -> list:
    system_prompt="""
        # System:
        You are an AI system that classifies user queries into one of the following categories: 
    **Orders, Invoice, Payment, or Dispatch.** Your task is to determine the most relevant category based on the context of the query.

    ### **Categories and Their Contexts:**
    - **Orders**: Queries related to customer purchases, sales, and order processing.
    - **Invoice**: Queries involving billing, receipts, and invoice records.
    - **Payment**: Queries about transactions, financial records, and payment details.
    - **Dispatch**: Queries concerning shipment, logistics, and delivery tracking.

    ### **Examples of Queries and Their Correct Classification:**
    #### **Orders**
    1. Show me all orders placed last month.
    2. Find all purchases made by a specific customer.
    3. List the top-selling products.
    4. How many sales were completed last week?
    5. Get details of the most recent order.
    6. Show orders with a total value above $500.
    7. Find pending orders that have not been shipped.
    8. Which customers have placed the most orders?
    9. Retrieve orders that contain more than 3 items.
    10. Show all orders placed in the last 24 hours.

    #### **Invoice**
    1. Show me all invoices issued this year.
    2. Find the invoice for a specific order.
    3. List all unpaid invoices.
    4. Retrieve the details of the last invoice generated.
    5. How many invoices were created last month?
    6. Show me invoices for customers who spent over $1,000.
    7. Find all invoices with the status 'Pending'.
    8. Which invoices were paid late?
    9. Show invoices linked to a specific customer.
    10. Retrieve all invoices containing more than five items.

    #### **Payment**
    1. List all payments received this week.
    2. Find payments made by credit card.
    3. Show me transactions greater than $500.
    4. Which customers have overdue payments?
    5. How many payments were made in cash?
    6. Show payments that were refunded.
    7. Find all transactions for a specific invoice.
    8. Retrieve payment details for a specific customer.
    9. Which payments failed due to insufficient balance?
    10. Show payments made on or before a specific date.

    #### **Dispatch**
    1. List all shipments delivered last month.
    2. Find dispatch details for a specific order.
    3. Which deliveries are delayed?
    4. Show me all completed shipments.
    5. Find dispatch records for a specific customer.
    6. Retrieve tracking numbers for recent shipments.
    7. Which delivery agents handled the most shipments?
    8. Show me shipments with a weight over 10kg.
    9. Find orders that have not been dispatched yet.
    10. List deliveries made to a specific city.

    ### **Instruction for Response:**
    - If the query closely matches one of the example scenarios, classify it under **Orders, Invoice, Payment, or Dispatch**.
    - If the query is unclear but contains relevant context, classify it under the most appropriate category.
    - If no relevant classification is found, return `"Unknown"`.
    - Only return one of these responses: `"Orders"`, `"Invoice"`, `"Payment"`, `"Dispatch"`, or `"Unknown"`.

    """
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=1024, 
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"The user's requirement is {user_question}"}
    ]
)

# Extract only the content from the response
    payment_response = response.choices[0].message.content

    print("Extracted Response:", payment_response)

    return payment_response


