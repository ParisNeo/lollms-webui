
import sqlite3
# =================================== Database ==================================================================
class DiscussionsDB:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path

    def populate(self):
        """
        create database schema
        """
        print("Checking discussions database...")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
        
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS discussion (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT
                    )
                """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS message (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT NOT NULL,
                        content TEXT NOT NULL,
                        discussion_id INTEGER NOT NULL,
                        FOREIGN KEY (discussion_id) REFERENCES discussion(id)
                    )
                """
                )
            conn.commit()

    def select(self, query, fetch_all=True):
        """
        Execute the specified SQL select query on the database,
        with optional parameters.
        Returns the cursor object for further processing.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
            

    def delete(self, query, fetch_all=True):
        """
        Execute the specified SQL delete query on the database,
        with optional parameters.
        Returns the cursor object for further processing.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
   
    def insert(self, query, params=None):
        """
        Execute the specified INSERT SQL query on the database,
        with optional parameters.
        Returns the ID of the newly inserted row.
        """
        
        with sqlite3.connect(self.db_path) as conn:
            self.conn = conn
            cursor = self.execute(query, params)
            rowid = cursor.lastrowid
            conn.commit()
        self.conn = None
        return rowid


    def create_discussion(self, title="untitled"):
        """Creates a new discussion

        Args:
            title (str, optional): The title of the discussion. Defaults to "untitled".

        Returns:
            Discussion: A Discussion instance 
        """
        discussion_id = self.insert(f"INSERT INTO discussion (title) VALUES ({title})")
        return Discussion(discussion_id, self)

    def build_discussion(self, discussion_id=0):
        return Discussion(discussion_id, self)

    def get_discussions(self):
        rows = self.select("SELECT * FROM discussion")
         
        return [{"id": row[0], "title": row[1]} for row in rows]

    def does_last_discussion_have_messages(self):
        last_message = self.select("SELECT * FROM message ORDER BY id DESC LIMIT 1", fetch_all=False)
        return last_message is not None
    
    def remove_discussions(self):
        self.delete("DELETE FROM message")
        self.delete("DELETE FROM discussion")


    def export_to_json(self):
        cur = self.execute("SELECT * FROM discussion")
        discussions = []
        for row in cur.fetchall():
            discussion_id = row[0]
            discussion = {"id": discussion_id, "messages": []}
            cur.execute("SELECT * FROM message WHERE discussion_id=?", (discussion_id,))
            for message_row in cur.fetchall():
                discussion["messages"].append(
                    {"sender": message_row[1], "content": message_row[2]}
                )
            discussions.append(discussion)
        return discussions


class Discussion:
    def __init__(self, discussion_id, discussions_db:DiscussionsDB):
        self.discussion_id = discussion_id
        self.discussions_db = discussions_db

    def add_message(self, sender, content):
        """Adds a new message to the discussion

        Args:
            sender (str): The sender name
            content (str): The text sent by the sender

        Returns:
            int: The added message id
        """
        self.discussions_db.execute(
            f"INSERT INTO message (sender, content, discussion_id) VALUES ({sender}, {content}, {self.discussion_id})",
        )
        message_id = self.discussions_db.conn.cursor().lastrowid
        self.discussions_db.commit()
        return message_id

    def rename(self, new_title):
        """Renames the discussion

        Args:
            new_title (str): The nex discussion name
        """
        self.discussions_db.execute(
            f"UPDATE discussion SET title={new_title} WHERE id={self.discussion_id}"
        )
        self.discussions_db.commit()

    def delete_discussion(self):
        """Deletes the discussion
        """
        self.discussions_db.execute(
            f"DELETE FROM message WHERE discussion_id={self.discussion_id}"
        )
        self.discussions_db.execute(
            f"DELETE FROM discussion WHERE id={self.discussion_id}"
        )
        self.discussions_db.commit()

    def get_messages(self):
        """Gets a list of messages information

        Returns:
            list: List of entries in the format {"sender":sender name, "content":message content,"id":message id}
        """
        rows = self.discussions_db.select(
            f"SELECT * FROM message WHERE discussion_id={self.discussion_id}"
        )
        return [{"sender": row[1], "content": row[2], "id": row[0]} for row in rows]

    def update_message(self, message_id, new_content):
        """Updates the content of a message

        Args:
            message_id (int): The id of the message to be changed
            new_content (str): The nex message content
        """
        self.discussions_db.execute(
            f"UPDATE message SET content = {new_content} WHERE id = {message_id}"
        )
        self.discussions_db.commit()


# ========================================================================================================================
