
import sqlite3
from pathlib import Path
__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"


# =================================== Database ==================================================================
class DiscussionsDB:
    MSG_TYPE_NORMAL         = 0
    MSG_TYPE_CONDITIONNING  = 1

    def __init__(self, db_path="database.db"):
        self.db_path = Path(db_path)
        self.db_path .parent.mkdir(exist_ok=True, parents= True)

    def populate(self):
        """
        create database schema
        """
        db_version = 3
        # Verify encoding and change it if it is not complient
        with sqlite3.connect(self.db_path) as conn:
            # Execute a PRAGMA statement to get the current encoding of the database
            cur = conn.execute('PRAGMA encoding')
            current_encoding = cur.fetchone()[0]

            if current_encoding != 'UTF-8':
                # The current encoding is not UTF-8, so we need to change it
                print(f"The current encoding is {current_encoding}, changing to UTF-8...")
                conn.execute('PRAGMA encoding = "UTF-8"')
                conn.commit()        

        print("Checking discussions database...")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            discussion_table_exist=False
            message_table_exist=False
            schema_table_exist=False

            # Check if the 'schema_version' table exists
            try:
                cursor.execute("""
                    CREATE TABLE schema_version (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version INTEGER NOT NULL
                    )
                """)
            except:
                schema_table_exist = True
            try:
                cursor.execute("""
                    CREATE TABLE discussion (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
            except Exception:
                discussion_table_exist=True        
            try:
                cursor.execute("""
                        CREATE TABLE message (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sender TEXT NOT NULL,
                            content TEXT NOT NULL,
                            type INT NOT NULL,
                            rank INT NOT NULL,
                            parent INT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            discussion_id INTEGER NOT NULL,
                            FOREIGN KEY (discussion_id) REFERENCES discussion(id),
                            FOREIGN KEY (parent) REFERENCES message(id)
                        )
                    """
                    )
            except :
                message_table_exist=True

            # Get the current version from the schema_version table
            cursor.execute("SELECT version FROM schema_version WHERE id = 1")
            row = cursor.fetchone()
            if row is None:
                # If the table is empty, assume version 0
                version = 0
            else:
                # Otherwise, use the version from the table
                version = row[0]

            # Upgrade the schema to version 1
            if version < 1:
                print(f"Upgrading schema to version {db_version}...")
                # Add the 'created_at' column to the 'message' table
                if message_table_exist:
                    cursor.execute("ALTER TABLE message ADD COLUMN type INT DEFAULT 0") # Added in V1
                    cursor.execute("ALTER TABLE message ADD COLUMN rank INT DEFAULT 0") # Added in V1
                    cursor.execute("ALTER TABLE message ADD COLUMN parent INT DEFAULT 0") # Added in V2
                    cursor.execute("ALTER TABLE message ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP") # Added in V3
                    cursor.execute("ALTER TABLE discussion ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP") # Added in V3
                    
            # Upgrade the schema to version 1
            elif version < 2:
                print(f"Upgrading schema to version {db_version}...")
                # Add the 'created_at' column to the 'message' table
                if message_table_exist:
                    try:
                        cursor.execute("ALTER TABLE message ADD COLUMN parent INT DEFAULT 0") # Added in V2
                        cursor.execute("ALTER TABLE message ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP") # Added in V3
                        cursor.execute("ALTER TABLE discussion ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP") # Added in V3
                    except :
                        pass
            # Upgrade the schema to version 1
            elif version < 3:
                print(f"Upgrading schema to version {db_version}...")
                # Add the 'created_at' column to the 'message' table
                if message_table_exist:
                    try:
                        cursor.execute("ALTER TABLE message ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP") # Added in V3
                        cursor.execute("ALTER TABLE discussion ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP") # Added in V3
                    except :
                        pass
            # Update the schema version
            if not schema_table_exist:
                cursor.execute(f"INSERT INTO schema_version (id, version) VALUES (1, {db_version})")
            else:
                cursor.execute(f"UPDATE schema_version SET version=? WHERE id=?",(db_version,1))

            conn.commit()

    def select(self, query, params=None, fetch_all=True):
        """
        Execute the specified SQL select query on the database,
        with optional parameters.
        Returns the cursor object for further processing.
        """
        with sqlite3.connect(self.db_path) as conn:
            if params is None:
                cursor = conn.execute(query)
            else:
                cursor = conn.execute(query, params)
            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
            

    def delete(self, query, params=None):
        """
        Execute the specified SQL delete query on the database,
        with optional parameters.
        Returns the cursor object for further processing.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            conn.commit()
   
    def insert(self, query, params=None):
        """
        Execute the specified INSERT SQL query on the database,
        with optional parameters.
        Returns the ID of the newly inserted row.
        """
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rowid = cursor.lastrowid
            conn.commit()
        self.conn = None
        return rowid

    def update(self, query, params=None):
        """
        Execute the specified Update SQL query on the database,
        with optional parameters.
        Returns the ID of the newly inserted row.
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()
    
    def load_last_discussion(self):
        last_discussion_id = self.select("SELECT id FROM discussion ORDER BY id DESC LIMIT 1", fetch_all=False)
        if last_discussion_id is None:
            last_discussion = self.create_discussion()
            last_discussion_id = last_discussion.discussion_id
        else:
            last_discussion_id = last_discussion_id[0]
        self.current_message_id = self.select("SELECT id FROM message WHERE discussion_id=? ORDER BY id DESC LIMIT 1", (last_discussion_id,), fetch_all=False)
        return Discussion(last_discussion_id, self)
    
    def create_discussion(self, title="untitled"):
        """Creates a new discussion

        Args:
            title (str, optional): The title of the discussion. Defaults to "untitled".

        Returns:
            Discussion: A Discussion instance 
        """
        discussion_id = self.insert(f"INSERT INTO discussion (title) VALUES (?)",(title,))
        return Discussion(discussion_id, self)

    def build_discussion(self, discussion_id=0):
        return Discussion(discussion_id, self)

    def get_discussions(self):
        rows = self.select("SELECT * FROM discussion")         
        return [{"id": row[0], "title": row[1]} for row in rows]

    def does_last_discussion_have_messages(self):
        last_discussion_id = self.select("SELECT id FROM discussion ORDER BY id DESC LIMIT 1", fetch_all=False)
        if last_discussion_id is None:
            last_discussion = self.create_discussion()
            last_discussion_id = last_discussion.discussion_id
        else:
            last_discussion_id = last_discussion_id[0]
        last_message = self.select("SELECT * FROM message WHERE discussion_id=?", (last_discussion_id,), fetch_all=False)
        return last_message is not None
    
    def remove_discussions(self):
        self.delete("DELETE FROM message")
        self.delete("DELETE FROM discussion")


    def export_to_json(self):
        db_discussions = self.select("SELECT * FROM discussion")
        discussions = []
        for row in db_discussions:
            discussion_id = row[0]
            discussion_title = row[1]
            discussion = {"id": discussion_id, "title":discussion_title, "messages": []}
            rows = self.select(f"SELECT * FROM message WHERE discussion_id=?",(discussion_id,))
            for message_row in rows:
                sender = message_row[1]
                content = message_row[2]
                content_type = message_row[3]
                rank = message_row[4]
                parent = message_row[5]
                discussion["messages"].append(
                    {"sender": sender, "content": content, "type": content_type, "rank": rank, "parent": parent}
                )
            discussions.append(discussion)
        return discussions

    def export_discussions_to_json(self, discussions_ids:list):
        # Convert the list of discussion IDs to a tuple
        discussions_ids_tuple = tuple(discussions_ids)
        txt = ','.join(['?'] * len(discussions_ids_tuple))
        db_discussions = self.select(
            f"SELECT * FROM discussion WHERE id IN ({txt})",
            discussions_ids_tuple
        )
        discussions = []
        for row in db_discussions:
            discussion_id = row[0]
            discussion_title = row[1]
            discussion = {"id": discussion_id, "title":discussion_title, "messages": []}
            rows = self.select(f"SELECT * FROM message WHERE discussion_id=?",(discussion_id,))
            for message_row in rows:
                sender = message_row[1]
                content = message_row[2]
                content_type = message_row[3]
                rank = message_row[4]
                parent = message_row[5]
                discussion["messages"].append(
                    {"sender": sender, "content": content, "type": content_type, "rank": rank, "parent": parent}
                )
            discussions.append(discussion)
        return discussions
    
    def import_from_json(self, json_data):
        discussions = []
        data = json_data
        for discussion_data in data:
            discussion_id = discussion_data.get("id")
            discussion_title = discussion_data.get("title")
            messages_data = discussion_data.get("messages", [])
            discussion = {"id": discussion_id, "title": discussion_title, "messages": []}

            # Insert discussion into the database
            discussion_id = self.insert("INSERT INTO discussion (title) VALUES (?)", (discussion_title,))

            for message_data in messages_data:
                sender = message_data.get("sender")
                content = message_data.get("content")
                content_type = message_data.get("type")
                rank = message_data.get("rank")
                parent = message_data.get("parent")
                discussion["messages"].append(
                    {"sender": sender, "content": content, "type": content_type, "rank": rank, "parent": parent}
                )

                # Insert message into the database
                self.insert("INSERT INTO message (sender, content, type, rank, parent, discussion_id) VALUES (?, ?, ?, ?, ?, ?)",
                            (sender, content, content_type, rank, parent, discussion_id))

            discussions.append(discussion)

        return discussions

class Discussion:
    def __init__(self, discussion_id, discussions_db:DiscussionsDB):
        self.discussion_id = discussion_id
        self.discussions_db = discussions_db

    def add_message(self, sender, content, message_type=0, rank=0, parent=0):
        """Adds a new message to the discussion

        Args:
            sender (str): The sender name
            content (str): The text sent by the sender

        Returns:
            int: The added message id
        """
        message_id = self.discussions_db.insert(
            "INSERT INTO message (sender, content, type, rank, parent, discussion_id) VALUES (?, ?, ?, ?, ?, ?)", 
            (sender, content, message_type, rank, parent, self.discussion_id)
        )
        return message_id

    def rename(self, new_title):
        """Renames the discussion

        Args:
            new_title (str): The nex discussion name
        """
        self.discussions_db.update(
            f"UPDATE discussion SET title=? WHERE id=?",(new_title,self.discussion_id)
        )

    def delete_discussion(self):
        """Deletes the discussion
        """
        self.discussions_db.delete(
            f"DELETE FROM message WHERE discussion_id={self.discussion_id}"
        )
        self.discussions_db.delete(
            f"DELETE FROM discussion WHERE id={self.discussion_id}"
        )

    def get_messages(self):
        """Gets a list of messages information

        Returns:
            list: List of entries in the format {"id":message id, "sender":sender name, "content":message content, "type":message type, "rank": message rank}
        """
        rows = self.discussions_db.select(
            "SELECT * FROM message WHERE discussion_id=?", (self.discussion_id,)
        )

        return [{"id": row[0], "sender": row[1], "content": row[2], "type": row[3], "rank": row[4], "parent": row[5]} for row in rows]

    def update_message(self, message_id, new_content):
        """Updates the content of a message

        Args:
            message_id (int): The id of the message to be changed
            new_content (str): The nex message content
        """
        self.discussions_db.update(
            f"UPDATE message SET content = ? WHERE id = ?",(new_content,message_id)
        )
    
    def message_rank_up(self, message_id):
        """Increments the rank of the message

        Args:
            message_id (int): The id of the message to be changed
        """
        # Retrieve current rank value for message_id
        current_rank = self.discussions_db.select("SELECT rank FROM message WHERE id=?", (message_id,),False)[0]

        # Increment current rank value by 1
        new_rank = current_rank + 1        
        self.discussions_db.update(
            f"UPDATE message SET rank = ? WHERE id = ?",(new_rank,message_id)
        )
        return new_rank

    def message_rank_down(self, message_id):
        """Increments the rank of the message

        Args:
            message_id (int): The id of the message to be changed
        """
        # Retrieve current rank value for message_id
        current_rank = self.discussions_db.select("SELECT rank FROM message WHERE id=?", (message_id,),False)[0]

        # Increment current rank value by 1
        new_rank = current_rank - 1        
        self.discussions_db.update(
            f"UPDATE message SET rank = ? WHERE id = ?",(new_rank,message_id)
        )
        return new_rank
    
    def delete_message(self, message_id):
        """Delete the message

        Args:
            message_id (int): The id of the message to be deleted
        """
        # Retrieve current rank value for message_id
        self.discussions_db.delete("DELETE FROM message WHERE id=?", (message_id,))

# ========================================================================================================================
