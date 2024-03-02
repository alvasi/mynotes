from flask import Flask, jsonify, request
import psycopg2 as psycopg
import os
from datetime import date
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# SQL
DB_HOST = "db.doc.ic.ac.uk"
DB_USER = "wss119"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "wss119"
DB_PORT = "5432"

today = date.today()


def get_db_connection():
    try:
        connection = psycopg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
        )
        return connection
    except (Exception, psycopg.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None


@app.route("/all_deadlines", methods=["GET"])
def get_all_deadlines():
    username = request.args.get("username")
    user_deadlines = {"entries": []}

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM deadlines WHERE userid = %s", (username,))
            records = cursor.fetchall()
            for record in records:
                record_dict = {
                    "id": record[0],
                    "task": record[2],
                    "date": record[3].strftime("%d/%m/%Y"),
                    "completed": record[4],
                }
                user_deadlines["entries"].append(record_dict)
        except (Exception, psycopg.Error) as error:
            print("Error retrieving deadlines: ", error)
        finally:
            connection.close()
    return jsonify(user_deadlines)


@app.route("/past_deadlines", methods=["GET"])
def get_past_deadlines():
    username = request.args.get("username")
    past_deadlines = {"entries": []}
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Select deadlines before today
            cursor.execute(
                "SELECT * FROM deadlines WHERE userid = %s AND (deadline < %s OR completed = 'true') ORDER BY deadline DESC",
                (
                    username,
                    today,
                ),
            )
            records = cursor.fetchall()
            for record in records:
                record_dict = {
                    "id": record[0],
                    "task": record[2],
                    "date": record[3].strftime("%d/%m/%Y"),
                    "completed": record[4],
                }
                past_deadlines["entries"].append(record_dict)
        except (Exception, psycopg.Error) as error:
            print("Error retrieving past deadlines: ", error)
        finally:
            connection.close()
    return jsonify(past_deadlines)


@app.route("/current_deadlines", methods=["GET"])
def get_current_deadlines():
    username = request.args.get("username")
    current_deadlines = {"entries": []}
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Select deadlines on today's date or in the future
            cursor.execute(
                "SELECT * FROM deadlines WHERE userid = %s AND deadline >= %s AND completed = 'false' ORDER BY deadline ASC",
                (
                    username,
                    today,
                ),
            )
            records = cursor.fetchall()
            for record in records:
                record_dict = {
                    "id": record[0],
                    "task": record[2],
                    "date": record[3].strftime("%d/%m/%Y"),
                    "completed": record[4],
                }
                current_deadlines["entries"].append(record_dict)
        except (Exception, psycopg.Error) as error:
            print("Error retrieving current deadlines: ", error)
        finally:
            connection.close()
    return jsonify(current_deadlines)


@app.route("/add_deadline", methods=["POST"])
def add_deadline():
    data = request.get_json()
    username = data.get("username")
    task = data.get("task")
    deadline = data.get("deadline")

    if not all([username, task, deadline]):
        return jsonify("Missing data"), 400

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            insert_sql = "INSERT INTO deadlines (userid, task, deadline, completed) VALUES (%s, %s, %s, 'false')"
            cursor.execute(insert_sql, (username, task, deadline))
            connection.commit()
            return jsonify("Deadline added successfully"), 201
        except (Exception, psycopg.Error) as error:
            print("Error while inserting data into PostgreSQL", error)
            return jsonify("Failed to add deadline"), 500
        finally:
            if connection is not None:
                connection.close()
    else:
        return jsonify("Failed to connect to the database"), 500


@app.route("/complete_deadline", methods=["POST"])
def complete_deadline():
    data = request.get_json()
    deadline_id = data.get("id")

    if not deadline_id:
        return jsonify("Missing deadline ID"), 400

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            update_sql = "UPDATE deadlines SET completed = 'true' WHERE id = %s"
            cursor.execute(update_sql, (deadline_id,))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify("No such deadline found"), 404
            return jsonify("Deadline marked as completed"), 200
        except (Exception, psycopg.Error) as error:
            print("Error while updating deadline in PostgreSQL", error)
            return jsonify("Failed to mark deadline as completed"), 500
        finally:
            if connection is not None:
                connection.close()
    else:
        return jsonify("Failed to connect to the database"), 500


if __name__ == "__main__":
    app.run(debug=True)
