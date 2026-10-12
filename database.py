import mysql.connector
from mysql.connector import Error

def create_connection():
    """Establishes a connection to the local MySQL server."""
    try:
        # Update these credentials to match your local MySQL setup
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_password', # Replace with your MySQL password
            database='culinary_agent_db'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def initialize_db():
    """Creates the database and the chat history table."""
    try:
        # Connect without specifying a database first to create it
        base_conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_password' # Replace with your MySQL password
        )
        cursor = base_conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS culinary_agent_db")
        base_conn.close()

        # Now connect to the specific database to create tables
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            table_query = """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(table_query)
            conn.commit()
            print("Database and tables initialized successfully.")
            conn.close()
    except Error as e:
        print(f"Failed to initialize database: {e}")

if __name__ == '__main__':
    initialize_db()