
import sqlite3
from pathlib import Path
from datetime import datetime
from lollms.helpers import ASCIIColors
import json

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"


# =================================== Database ==================================================================
class DiscussionsDB:
    
    def __init__(self, db_path="database.db"):
        self.db_path = Path(db_path)
        self.db_path .parent.mkdir(exist_ok=True, parents= True)


    def create_tables(self):
        db_version = 9
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discussion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    binding TEXT,
                    model TEXT,
                    personality TEXT,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type INT NOT NULL,
                    sender_type INT DEFAULT 0,
                    rank INT NOT NULL DEFAULT 0,
                    parent_message_id INT,
                    created_at TIMESTAMP,
                    finished_generating_at TIMESTAMP,
                    discussion_id INTEGER NOT NULL,
                    metadata TEXT,
                    ui TEXT,
                    FOREIGN KEY (discussion_id) REFERENCES discussion(id),
                    FOREIGN KEY (parent_message_id) REFERENCES message(id)
                )
            """)

            cursor.execute("SELECT * FROM schema_version")
            row = cursor.fetchone()

            if row is None:
                cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (db_version,))
            else:
                cursor.execute("UPDATE schema_version SET version = ?", (db_version,))            

            conn.commit()

    def add_missing_columns(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            table_columns = {
                'discussion': [
                    'id',
                    'title',
                    'created_at'
                ],
                'message': [
                    'id',
                    'binding',
                    'model',
                    'personality',
                    'sender',
                    'content',
                    'message_type',
                    'sender_type',
                    'rank',
                    'parent_message_id',
                    'created_at',
                    'metadata',
                    'ui',
                    'finished_generating_at',
                    'discussion_id'
                ]
            }

            for table, columns in table_columns.items():
                cursor.execute(f"PRAGMA table_info({table})")
                existing_columns = [column[1] for column in cursor.fetchall()]

                for column in columns:
                    if column not in existing_columns:
                        if column == 'id':
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER PRIMARY KEY AUTOINCREMENT")
                        elif column.endswith('_at'):
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} TIMESTAMP")
                        elif column=='metadata':
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT")
                        elif column=='message_type':
                            cursor.execute(f"ALTER TABLE {table} RENAME COLUMN type TO {column}")
                        elif column=='sender_type':
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INT DEFAULT 0")
                        elif column=='parent_message_id':
                            cursor.execute(f"ALTER TABLE {table} RENAME COLUMN parent TO {column}")
                        else:
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT")
                        ASCIIColors.yellow(f"Added column :{column}")
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

    def update(self, query, params:tuple=None):
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
            rows = self.select(f"SELECT sender, content, type, rank, parent_message_id, binding, model, personality, created_at, finished_generating_at FROM message WHERE discussion_id=?",(discussion_id,))
            for message_row in rows:
                sender = message_row[1]
                content = message_row[2]
                content_type = message_row[3]
                rank = message_row[4]
                parent_message_id = message_row[5]
                binding = message_row[6]
                model = message_row[7]
                personality = message_row[8]
                created_at = message_row[9]
                finished_generating_at = message_row[10]
                
                discussion["messages"].append(
                    {"sender": sender, "content": content, "type": content_type, "rank": rank, "parent_message_id": parent_message_id, "binding": binding, "model":model, "personality":personality, "created_at":created_at, "finished_generating_at":finished_generating_at}
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
            rows = self.select(f"SELECT sender, content, type, rank, parent_message_id, binding, model, personality, created_at, finished_generating_at FROM message WHERE discussion_id=?",(discussion_id,))
            for message_row in rows:
                sender = message_row[0]
                content = message_row[1]
                content_type = message_row[2]
                rank = message_row[3]
                parent_message_id = message_row[4]
                binding = message_row[5]
                model = message_row[6]
                personality = message_row[7]
                created_at = message_row[8]
                finished_generating_at = message_row[9]
                
                discussion["messages"].append(
                    {"sender": sender, "content": content, "type": content_type, "rank": rank, "parent_message_id": parent_message_id, "binding": binding, "model":model, "personality":personality, "created_at":created_at, "finished_generating_at": finished_generating_at}
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
                parent_message_id = message_data.get("parent_message_id")
                binding = message_data.get("binding","")
                model = message_data.get("model","")
                personality = message_data.get("personality","")
                created_at = message_data.get("created_at",datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                finished_generating_at = message_data.get("finished_generating_at",datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                discussion["messages"].append(
                    {"sender": sender, "content": content, "type": content_type, "rank": rank, "binding": binding, "model": model, "personality": personality, "created_at": created_at, "finished_generating_at": finished_generating_at}
                )

                # Insert message into the database
                self.insert("INSERT INTO message (sender, content, type, rank, parent_message_id, binding, model, personality, created_at, finished_generating_at, discussion_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (sender, content, content_type, rank, parent_message_id, binding, model, personality, created_at, finished_generating_at, discussion_id))

            discussions.append(discussion)

        return discussions


class Message:
    def __init__(
                    self,
                    discussion_id,
                    discussions_db,
                    message_type,
                    sender_type,
                    sender,
                    content,
                    metadata                = None,
                    ui                      = None,
                    rank                    = 0,
                    parent_message_id       = 0,
                    binding                 = "",
                    model                   = "",
                    personality             = "",
                    created_at              = None,
                    finished_generating_at  = None,
                    id                      = None,
                    insert_into_db          = False
                    ):
        
        self.discussion_id = discussion_id
        self.discussions_db = discussions_db
        self.self = self
        self.sender = sender
        self.sender_type = sender_type
        self.content = content
        self.message_type = message_type
        self.rank = rank
        self.parent_message_id = parent_message_id
        self.binding = binding
        self.model = model
        self.metadata = json.dumps(metadata, indent=4) if metadata is not None and type(metadata)== dict else metadata
        self.ui = ui
        self.personality = personality
        self.created_at = created_at
        self.finished_generating_at = finished_generating_at

        if insert_into_db:
            self.id = self.discussions_db.insert(
                "INSERT INTO message (sender,  message_type,  sender_type,  sender,  content,  metadata, ui,  rank,  parent_message_id,  binding,  model,  personality,  created_at,  finished_generating_at,  discussion_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (sender, message_type, sender_type, sender, content, metadata, ui, rank, parent_message_id, binding, model, personality, created_at, finished_generating_at, discussion_id)
            )
        else:
            self.id = id


    @staticmethod
    def get_fields():
        return [
            "id",
            "message_type",
            "sender_type",
            "sender",
            "content",
            "metadata",
            "ui",
            "rank",
            "parent_message_id",
            "binding",
            "model",
            "personality",
            "created_at",
            "finished_generating_at",
            "discussion_id"
        ]        

    @staticmethod
    def from_db(discussions_db, message_id):
        columns = Message.get_fields()
        rows = discussions_db.select(
            f"SELECT {','.join(columns)} FROM message WHERE id=?", (message_id,)
        )
        data_dict={
            col:rows[0][i]
            for i,col in enumerate(columns)
        }
        data_dict["discussions_db"]=discussions_db
        return Message(
            **data_dict
        )

    @staticmethod
    def from_dict(discussions_db,data_dict):
        data_dict["discussions_db"]=discussions_db
        return Message(
            **data_dict
        )

    def insert_into_db(self):
        self.message_id = self.discussions_db.insert(
            "INSERT INTO message (sender, content, metadata, ui, type, rank, parent_message_id, binding, model, personality, created_at, finished_generating_at, discussion_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (self.sender, self.content, self.metadata, self.ui, self.message_type, self.rank, self.parent_message_id, self.binding, self.model, self.personality, self.created_at, self.finished_generating_at, self.discussion_id)
        )

    def update_db(self):
        self.message_id = self.discussions_db.insert(
            "INSERT INTO message (sender, content, metadata, ui, type, rank, parent_message_id, binding, model, personality, created_at, finished_generating_at, discussion_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (self.sender, self.content, self.metadata, self.ui, self.message_type, self.rank, self.parent_message_id, self.binding, self.model, self.personality, self.created_at, self.finished_generating_at, self.discussion_id)
        )
    def update(self, new_content, new_metadata=None, new_ui=None, commit=True):
        self.finished_generating_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        text = f"UPDATE message SET content = ?"
        params = [new_content]
        if new_metadata is not None:
            text+=", metadata = ?"
            params.append(new_metadata)
        if new_ui is not None:
            text+=", ui = ?"
            params.append(new_ui)

        text +=", finished_generating_at = ? WHERE id = ?"
        params.append(self.finished_generating_at)
        params.append(self.id)
        self.discussions_db.update(
            text, tuple(params)
        )        

    def to_json(self):
        attributes = Message.get_fields()
        msgJson = {}
        for attribute_name in attributes:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_name=="metadata":
                if type(attribute_value) == str:
                    msgJson[attribute_name] = json.loads(attribute_value)
                else:
                    msgJson[attribute_name] = attribute_value
            else:
                msgJson[attribute_name] = attribute_value
        return msgJson

class Discussion:
    def __init__(self, discussion_id, discussions_db:DiscussionsDB):
        self.discussion_id = discussion_id
        self.discussions_db = discussions_db
        self.messages = self.get_messages()
        if len(self.messages)>0:
            self.current_message = self.messages[-1]

    def load_message(self, id):
        """Gets a list of messages information

        Returns:
            list: List of entries in the format {"id":message id, "sender":sender name, "content":message content, "type":message type, "rank": message rank}
        """
        self.current_message = Message.from_db(self.discussions_db, id)
        return self.current_message
    
    def add_message(
                    self, 
                    message_type,
                    sender_type,
                    sender,
                    content,
                    metadata=None,
                    ui=None,
                    rank=0, 
                    parent_message_id=0, 
                    binding="", 
                    model ="", 
                    personality="", 
                    created_at=None, 
                    finished_generating_at=None
                ):
        """Adds a new message to the discussion

        Args:
            sender (str): The sender name
            content (str): The text sent by the sender

        Returns:
            int: The added message id
        """
        if created_at is None:
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        if finished_generating_at is None:
            finished_generating_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.current_message = Message(
            self.discussion_id,
            self.discussions_db,
            message_type,
            sender_type,
            sender,
            content,
            metadata,
            ui,
            rank,
            parent_message_id,
            binding,
            model,
            personality,
            created_at,
            finished_generating_at,
            insert_into_db=True
        )

        self.messages.append(self.current_message)

        return self.current_message

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
        columns = Message.get_fields()

        rows = self.discussions_db.select(
            f"SELECT {','.join(columns)} FROM message WHERE discussion_id=?", (self.discussion_id,)
        )
        msg_dict = [{ c:row[i] for i,c in enumerate(columns)} for row in rows]
        self.messages=[]
        for msg in msg_dict:
            self.messages.append(Message.from_dict(self.discussions_db, msg))

        if len(self.messages)>0:
            self.current_message = self.messages[-1]

        return self.messages

    def get_message(self, message_id):
        for message in self.messages:
            if message.id == int(message_id):
                self.current_message = message
                return message
        return None

    def select_message(self, message_id):
        msg = self.get_message(message_id)
        if msg is not None:
            self.current_message = msg
            return True
        else:
            return False 

    def update_message(self, new_content, new_metadata=None, new_ui=None):
        """Updates the content of a message

        Args:
            message_id (int): The id of the message to be changed
            new_content (str): The nex message content
        """
        self.current_message.update(new_content, new_metadata, new_ui)

    def edit_message(self, message_id, new_content, new_metadata=None, new_ui=None):
        """Edits the content of a message

        Args:
            message_id (int): The id of the message to be changed
            new_content (str): The nex message content
        """
        msg = self.get_message(message_id)
        if msg:
            msg.update(new_content, new_metadata, new_ui)
            return True
        else:
            return False


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
