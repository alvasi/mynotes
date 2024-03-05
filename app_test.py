import unittest
import psycopg2 as psycopg
from dotenv import load_dotenv
from app import app, get_db_connection
from unittest.mock import patch, MagicMock
from datetime import date
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


class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # Configure the app for testing
        app.config["TESTING"] = True
        self.client = app.test_client()

    # Example of a mock function to replace the actual database connection
    def mock_get_db_connection():
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "user1", "Task 1", date(2024,12,20), "false"),
        ]
        return mock_conn

    # test for the /all_deadlines endpoint
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_all_deadlines(self, mock_get_db_connection):
        response = self.client.get("/all_deadlines?username=user1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data["entries"]), 1)  # Assume one entry returned

    # test for the /past_deadlines endpoint
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_past_deadlines(self, mock_get_db_connection):
        response = self.client.get("/past_deadlines?username=user1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data["entries"]), 0)

    # test for the /current_deadlines endpoint
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_current_deadlines(self, mock_get_db_connection):
        response = self.client.get("/current_deadlines?username=user1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data["entries"]), 1)

    # test for the /add_deadline endpoint
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_add_deadline(self, mock_get_db_connection):
        mock_get_db_connection.return_value.cursor.return_value.rowcount = 1
        response = self.client.post(
            "/add_deadline",
            json={"username": "user1", "task": "New Task", "deadline": "2023-05-01"},
        )
        self.assertEqual(response.status_code, 201)

    # test for the /delete_deadlines endpoint
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_delete_deadline(self, mock_get_db_connection):
        mock_get_db_connection.return_value.cursor.return_value.rowcount = 1
        response = self.client.post("/delete_deadline", json={"id": 1})
        self.assertEqual(response.status_code, 200)

    # test for the /update_deadline endpoint
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_update_deadline(self, mock_get_db_connection):
        mock_get_db_connection.return_value.cursor.return_value.rowcount = 1
        response = self.client.post(
            "/update_deadline",
            json={"id": 1, "task": "Updated Task", "date": "2023-05-02"},
        )
        self.assertEqual(response.status_code, 200)

    # test for the /complete_deadline endpoint  
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_complete_deadline(self, mock_get_db_connection):
        mock_get_db_connection.return_value.cursor.return_value.rowcount = 1
        response = self.client.post("/complete_deadline", json={"id": 1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, "Deadline marked as completed")

    # test for the /mark_incomplete endpoint
    @patch("app.get_db_connection", side_effect=mock_get_db_connection)
    def test_mark_incomplete(self, mock_get_db_connection):
        mock_get_db_connection.return_value.cursor.return_value.rowcount = 1
        response = self.client.post("/mark_incomplete", json={"id": 1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, "Deadline marked as incomplete") 


if __name__ == "__main__":
    unittest.main()
