import sqlite3
import os

class HelpManager:
    """Manages the connection and fetching of help /tutorials from the help database"""

    def __init__(self, db_name="tutorial.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, "resources", db_name)
        self.connection = None
        self._connect()

    def _connect(self):
        """Connection to the database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            print(f"Connected to the tutorial database at {self.db_path}")
        except sqlite3.Error as e:
            print(f"An error occured connecting to the database: {str(e)}")
            self.connection = None

    def get_help_topic(self, topic_id: str):
        """Fetches the topic from the database that user requests
        
        Args:
            topic_id (str): The unique id for the topic

        Returns:
            tuple: (title, description, image_url, link) or (None, None, None, None) if not found
        """
        if not self.connection:
            print(f"No Database connection")
            return None, None, None, None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT title, description, link FROM help_topics WHERE topic_Id = ?", (topic_id,)
            )
            row = cursor.fetchone()
            if row:
                return row["title"], row["description"], row["image_url"], row["link"]
            else:
                print(f"No topic found with topic_id: {topic_id}")
                return None, None, None, None
        except sqlite3.Error as e:
            print(f"Error fetching data for topic_id '{topic_id}: ERROR: {str(e)}'")
            return None, None, None, None
    
    def close(self):
        """Close the connection to database"""
        if self.connection:
            self.connection.close()
            self.connection = None