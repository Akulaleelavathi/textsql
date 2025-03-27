EXAMPLE_QUERIES = {
    "zoai_invoice_report": {
        "What is the latest invoice amount of raju?": 
            "SELECT invoiceamount FROM invoices WHERE customername = 'raju' ORDER BY invoicedate DESC LIMIT 1;",
        
        "Show me the latest invoice details of raju.": 
            "SELECT * FROM invoices WHERE customername = 'raju' ORDER BY invoicedate DESC LIMIT 1;",
        
        "What was the last invoice generated for firm name?": 
            "SELECT * FROM invoices WHERE firmname = 'firm name' ORDER BY invoicedate DESC LIMIT 1;"
    }
}