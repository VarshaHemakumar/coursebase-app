# # db_config.py
# import psycopg2



# def get_connection():
#     return psycopg2.connect(
#         host="localhost",
#         database="coursebase",
#         user="postgres",
#         password="Sha@6379"
#     )

# if __name__ == "__main__":
#     try:
#         conn = get_connection()
#         print("Connected to PostgreSQL successfully!")
#         conn.close()
#     except Exception as e:
#         print("Connection failed:", e)



import os
import psycopg2
from urllib.parse import urlparse
# db_config.py

import os
from sqlalchemy import create_engine

def get_connection():
    """
    Returns a SQLAlchemy engine using the DATABASE_URL from environment variables.
    This is used for safe and efficient database access, especially with pandas.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set.")
    return create_engine(db_url)

# Optional: test connection when run directly
if __name__ == "__main__":
    try:
        engine = get_engine()
        with engine.connect() as conn:
            print(" Connected to PostgreSQL successfully!")
    except Exception as e:
        print(" Connection failed:", e)
