import os
import os
from urllib.parse import quote_plus

password = "Service@007"
encoded_password = quote_plus(password)

DATABASE_URL = os.getenv(
    "REDSHIFT_DB_URL",
    # f"redshift+psycopg2://zonoservice:{encoded_password}@zono-digital-redshift-cluster.c5m55gnwhus9.ap-south-1.redshift.amazonaws.com:5439/qa"
     f"redshift+psycopg2://zonoservice:{encoded_password}@localhost:5440/qa"
)

OPENAI_API_KEY = os.getenv("3fa63f591fde45c6a32b9dc06e2af714")

