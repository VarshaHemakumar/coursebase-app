# db_config.py
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="Sha@6379",
        dbname="coursebase"
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Connected to PostgreSQL successfully!")
        conn.close()
    except Exception as e:
        print("Connection failed:", e)
