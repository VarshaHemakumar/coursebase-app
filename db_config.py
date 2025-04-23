# # db_config.py
# import psycopg2



# def get_connection():
#     return psycopg2.connect(
#         host="dpg-d04kmuili9vc73esiovg-a",
#         database="course_base_db",
#         user="course_base_db_user",
#         password="quRSEUUv6KTm8eXocsY7eDW4pWRWQ4rE"
#     )

# if __name__ == "__main__":
#     try:
#         conn = get_connection()
#         print("Connected to PostgreSQL successfully!")
#         conn.close()
#     except Exception as e:
#         print("Connection failed:", e)

# db_config.py

import os
import psycopg2
from urllib.parse import urlparse

def get_connection():
    # Fetch the DATABASE_URL from environment variables
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Parse the URL into components
    result = urlparse(db_url)

    return psycopg2.connect(
        dbname=result.path[1:],        # Remove leading slash
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        print(" Connected to PostgreSQL successfully!")
        conn.close()
    except Exception as e:
        print(" Connection failed:", e)
