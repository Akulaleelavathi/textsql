import os

DATABASE_URL = os.getenv("REDSHIFT_DB_URL", "postgresql://username:password@redshift-cluster-url:5439/dbname")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key")
# export REDSHIFT_DB_URL="postgresql://username:password@redshift-cluster-url:5439/dbname"
# export OPENAI_API_KEY="your-api-key"
