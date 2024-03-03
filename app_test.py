import os
import unittest
import psycopg2 as psycopg
from dotenv import load_dotenv
from app import get_db_connection  

# Load environment variables from .env file
load_dotenv()

class TestDatabaseConnection(unittest.TestCase):
    def test_db_connection(self):
        """Test database connection."""
        try:
            connection = get_db_connection()
            # If we can get the server version, we have a working connection
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print("Connected to PostgreSQL version:", db_version)
        except psycopg.Error as e:
            self.fail("PostgreSQL Error: " + str(e))
        finally:
            if connection:
                connection.close()
                print("Database connection closed.")

if __name__ == '__main__':
    unittest.main()
