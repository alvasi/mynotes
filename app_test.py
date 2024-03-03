import unittest
import psycopg2 as psycopg
from dotenv import load_dotenv
from app import app, get_db_connection
from flask import json

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

class FlaskTestCase(unittest.TestCase):

    # This will run before every test
    def setUp(self):
        # Set up the app to use the testing configuration
        app.config['TESTING'] = True
        self.app = app.test_client()


    def test_all_deadlines(self):
        # Simulate a request to the /all_deadlines endpoint
        response = self.app.get('/all_deadlines?username=testuser')

        # Check if the response is OK
        self.assertEqual(response.status_code, 200)

        # Optionally, check if the data returned is correct
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertIn('entries', data)



if __name__ == '__main__':
    unittest.main()
