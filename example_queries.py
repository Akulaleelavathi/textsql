EXAMPLE_QUERIES = {
    "Basic Queries": {
        "What is the latest invoice amount of [customer name]?": 
            "SELECT invoiceamount FROM invoices WHERE customername = '[customer name]' ORDER BY invoicedate DESC LIMIT 1;",
        
        "Show me the latest invoice details of [customer name].": 
            "SELECT * FROM invoices WHERE customername = '[customer name]' ORDER BY invoicedate DESC LIMIT 1;",
        
        "What was the last invoice generated for [firm name]?": 
            "SELECT * FROM invoices WHERE firmname = '[firm name]' ORDER BY invoicedate DESC LIMIT 1;"
    },

    "Invoice Status & Amount": {
        "What is the total invoice amount for [customer name]?": 
            "SELECT SUM(invoiceamount) AS total_invoice_amount FROM invoices WHERE customername = '[customer name]';",
        
        "How many invoices are Pending for [customer name]?": 
            "SELECT COUNT(*) AS pending_invoice_count FROM invoices WHERE customername = '[customer name]' AND invoicestatus = 'PD';",
        
        "Show me all Paid invoices for [firm name].": 
            "SELECT * FROM invoices WHERE firmname = '[firm name]' AND invoicestatus = 'P';",
        
        "How many invoices are Partially Paid for [customer name]?": 
            "SELECT COUNT(*) AS partially_paid_invoice_count FROM invoices WHERE customername = '[customer name]' AND invoicestatus = 'PP';"
    },

    "Date-Based Queries": {
        "Show me all invoices generated today.": 
            "SELECT * FROM invoices WHERE invoicedate = CURRENT_DATE;",
        
        "How many invoices were created this month?": 
            "SELECT COUNT(*) AS invoice_count FROM invoices WHERE MONTH(invoicedate) = MONTH(CURRENT_DATE) AND YEAR(invoicedate) = YEAR(CURRENT_DATE);",
        
        "What is the total invoice amount generated in the last 3 months?": 
            "SELECT SUM(invoiceamount) AS total_invoice_amount FROM invoices WHERE invoicedate >= DATE_SUB(CURRENT_DATE, INTERVAL 3 MONTH);",
        
        "Show me all invoices generated between [start date] and [end date].": 
            "SELECT * FROM invoices WHERE invoicedate BETWEEN '[start date]' AND '[end date]';"
    },

    "Invoice Reference & Tracking": {
        "Find the invoice with reference number [invoice ref number].": 
            "SELECT * FROM invoices WHERE invoicerefnumber = '[invoice ref number]';",
        
        "What is the invoice amount for invoice ID [invoiceid]?": 
            "SELECT invoiceamount FROM invoices WHERE invoiceid = '[invoiceid]';",
        
        "Show me the invoices updated in the last 7 days.": 
            "SELECT * FROM invoices WHERE updated_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);"
    },

    "Customer Insights": {
        "Who is the top customer based on total invoice amount?": 
            "SELECT customername, SUM(invoiceamount) AS total_invoice_amount FROM invoices GROUP BY customername ORDER BY total_invoice_amount DESC LIMIT 1;",
        
        "List the customers who have the highest number of unpaid invoices.": 
            "SELECT customername, COUNT(*) AS unpaid_invoice_count FROM invoices WHERE invoicestatus = 'PD' GROUP BY customername ORDER BY unpaid_invoice_count DESC LIMIT 5;",
        
        "Which customer has the most invoices in the last 6 months?": 
            "SELECT customername, COUNT(*) AS invoice_count FROM invoices WHERE invoicedate >= DATE_SUB(CURRENT_DATE, INTERVAL 6 MONTH) GROUP BY customername ORDER BY invoice_count DESC LIMIT 1;"
    },

    "Firm Insights": {
        "Which firm has the most total invoiced amount?": 
            "SELECT firmname, SUM(invoiceamount) AS total_invoice_amount FROM invoices GROUP BY firmname ORDER BY total_invoice_amount DESC LIMIT 1;",
        
        "Show me all invoices generated for [firm name] in [year].": 
            "SELECT * FROM invoices WHERE firmname = '[firm name]' AND YEAR(invoicedate) = '[year]';"
    },

    "Workspace-Based Queries": {
        "Show all invoices belonging to workspace [workspaceid].": 
            "SELECT * FROM invoices WHERE workspaceid = '[workspaceid]';",
        
        "What is the total invoice amount for workspace [workspaceid] in the last month?": 
            "SELECT SUM(invoiceamount) AS total_invoice_amount FROM invoices WHERE workspaceid = '[workspaceid]' AND invoicedate >= DATE_SUB(CURRENT_DATE, INTERVAL 1 MONTH);"
    }
}
