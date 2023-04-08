
import sqlite3
# =================================== Database ==================================================================
class Discussion:
    def __init__(self, discussion_id, db_path="database.db"):
        self.discussion_id = discussion_id
        self.db_path = db_path

    @staticmethod
    def create_discussion(db_path="database.db", title="untitled"):
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO discussion (title) VALUES (?)", (title,))
            discussion_id = cur.lastrowid
            conn.commit()
        return Discussion(discussion_id, db_path)

    @staticmethod
    def get_discussion(db_path="database.db", discussion_id=0):
        return Discussion(discussion_id, db_path)

    def add_message(self, sender, content):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO message (sender, content, discussion_id) VALUES (?, ?, ?)",
                (sender, content, self.discussion_id),
            )
            message_id = cur.lastrowid
            conn.commit()
        return message_id

    @staticmethod
    def get_discussions(db_path):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM discussion")
            rows = cursor.fetchall()
        return [{"id": row[0], "title": row[1]} for row in rows]

    @staticmethod
    def rename(db_path, discussion_id, title):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE discussion SET title=? WHERE id=?", (title, discussion_id)
            )
            conn.commit()

    def delete_discussion(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM message WHERE discussion_id=?", (self.discussion_id,)
            )
            cur.execute("DELETE FROM discussion WHERE id=?", (self.discussion_id,))
            conn.commit()

    def get_messages(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM message WHERE discussion_id=?", (self.discussion_id,)
            )
            rows = cur.fetchall()
        return [{"sender": row[1], "content": row[2], "id": row[0]} for row in rows]

    def update_message(self, message_id, new_content):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE message SET content = ? WHERE id = ?", (new_content, message_id)
            )
            conn.commit()

    def remove_discussion(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.cursor().execute(
                "DELETE FROM discussion WHERE id=?", (self.discussion_id,)
            )
            conn.commit()


def last_discussion_has_messages(db_path="database.db"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM message ORDER BY id DESC LIMIT 1")
        last_message = cursor.fetchone()
    return last_message is not None


def export_to_json(db_path="database.db"):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM discussion")
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


def remove_discussions(db_path="database.db"):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM message")
        cur.execute("DELETE FROM discussion")
        conn.commit()


# create database schema
def check_discussion_db(db_path):
    print("Checking discussions database...")
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS discussion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT
            )
        """
        )
        cur.execute(
            """
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

    print("Ok")


# ========================================================================================================================
