import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

class DatabaseConnection:
    def __init__(self):
        # Database configuration
        self.config = {
            'host': 'localhost',
            'user': 'root',  # Change this to your MySQL username
            'password': 'root',  # Change this to your MySQL password
            'database': 'mood_tracker'
        }
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            print("Please make sure:")
            print("1. MySQL is installed and running")
            print("2. The database 'mood_tracker' exists")
            print("3. The username and password are correct")
            raise

    def save_mood_entry(self, date, text_input, voice_input, sentiment_score, mood_category):
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO mood_entries 
                      (date, text_input, voice_input, sentiment_score, mood_category) 
                      VALUES (%s, %s, %s, %s, %s)"""
            values = (date, text_input, voice_input, sentiment_score, mood_category)
            cursor.execute(query, values)
            self.connection.commit()
            print("Mood entry saved successfully")
        except Error as e:
            print(f"Error saving mood entry: {e}")
        finally:
            cursor.close()

    def get_daily_analysis(self, date):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """SELECT * FROM daily_analysis WHERE date = %s"""
            cursor.execute(query, (date,))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error getting daily analysis: {e}")
            return None
        finally:
            cursor.close()

    def get_weekly_analysis(self, start_date):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """SELECT * FROM weekly_analysis WHERE week_start_date = %s"""
            cursor.execute(query, (start_date,))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error getting weekly analysis: {e}")
            return None
        finally:
            cursor.close()

    def get_mood_entries_by_date_range(self, start_date, end_date):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """SELECT * FROM mood_entries 
                      WHERE date BETWEEN %s AND %s 
                      ORDER BY date"""
            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Error getting mood entries: {e}")
            return []
        finally:
            cursor.close()

    def close(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed") 