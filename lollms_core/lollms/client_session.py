from lollms.generation import RECEPTION_MANAGER, ROLE_CHANGE_DECISION, ROLE_CHANGE_OURTPUT
from lollms.databases.discussions_database import Discussion, DiscussionsDB
from lollms.paths import LollmsPaths
from threading import Thread

class Client:
    def __init__(self, lollms_paths:LollmsPaths, client_id:str, discussion:Discussion, db:DiscussionsDB):
        self.client_id = client_id
        self.discussion = discussion
        self.lollms_paths = lollms_paths

        if discussion:
            self.discussion_path = lollms_paths.personal_discussions_path/db.discussion_db_name/f"{discussion.discussion_id}"
        else:
            self.discussion_path = None
        self.db_name = db
        self.rooms = set()

        self.rag_databases = []
        self.generated_text = ""
        self.cancel_generation = False
        self.generation_routine:Thread = None
        self.processing = False
        self.schedule_for_deletion = False
        self.continuing = False
        self.first_chunk = True
        self.reception_manager = RECEPTION_MANAGER()  # Assuming RECEPTION_MANAGER is a global class

    def join_room(self, room_id:str):
        self.rooms.add(room_id)

    def leave_room(self, room_id:str):
        if room_id in self.rooms:
            self.rooms.remove(room_id)


class Session:
    def __init__(self, lollms_paths:LollmsPaths):
        self.clients = {}
        self.lollms_paths = lollms_paths

    def add_client(self, client_id, room_id:str, discussion:Discussion, db:DiscussionsDB):
        if client_id not in self.clients:
            self.clients[client_id] = Client(self.lollms_paths, client_id, discussion, db)
        
        self.clients[client_id].join_room(room_id)

    def get_client(self, client_id)->Client:
        return self.clients.get(client_id)

    def remove_client(self, client_id, room_id):
        client = self.get_client(client_id)
        if client:
            client.leave_room(room_id)
            if not client.rooms:
                del self.clients[client_id]
