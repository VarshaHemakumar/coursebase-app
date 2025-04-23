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

def get_connection():
    """
    Returns a psycopg2 connection using DATABASE_URL from environment variable.
    Safe for raw SQL execution with .cursor().
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set.")

    result = urlparse(db_url)

    return psycopg2.connect(
        dbname=result.path[1:],        
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

# Optional test connection
if __name__ == "__main__":
    try:
        conn = get_connection()
        print(" Connected to PostgreSQL successfully!")
        conn.close()
    except Exception as e:
        print(" Connection failed:", e)
