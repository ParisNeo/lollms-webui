from api.db import Discussion
from lollms.helpers import ASCIIColors
from flask import jsonify, request


def export_multiple_discussions(self):
        data = request.get_json()
        discussion_ids = data["discussion_ids"]
        discussions = self.db.export_discussions_to_json(discussion_ids)
        return jsonify(discussions)
          
def import_multiple_discussions(self):
    discussions = request.get_json()["jArray"]
    self.db.import_from_json(discussions)
    return jsonify(discussions)

def rename(self):
    data = request.get_json()
    client_id = data["client_id"]
    title = data["title"]
    self.connections[client_id]["current_discussion"].rename(title)
    return "renamed successfully"

def edit_title(self):
    data                = request.get_json()
    client_id           = data["client_id"]
    title               = data["title"]
    discussion_id       = data["id"]
    self.connections[client_id]["current_discussion"] = Discussion(discussion_id, self.db)
    self.connections[client_id]["current_discussion"].rename(title)
    return jsonify({'status':True})

def delete_discussion(self):
    data            = request.get_json()
    client_id       = data["client_id"]
    discussion_id   = data["id"]
    self.connections[client_id]["current_discussion"] = Discussion(discussion_id, self.db)
    self.connections[client_id]["current_discussion"].delete_discussion()
    self.connections[client_id]["current_discussion"] = None
    return jsonify({'status':True})

def edit_message(self):
    client_id       = request.args.get("client_id")
    message_id      = request.args.get("id")
    new_message     = request.args.get("message")
    try:
        self.connections[client_id]["current_discussion"].edit_message(message_id, new_message)
        return jsonify({"status": True})
    except Exception as ex:
        trace_exception(ex)
        return jsonify({"status": False, "error":str(ex)})


def message_rank_up(self):
    client_id       = request.args.get("client_id")
    discussion_id   = request.args.get("id")
    try:
        new_rank = self.connections[client_id]["current_discussion"].message_rank_up(discussion_id)
        return jsonify({"status": True, "new_rank": new_rank})
    except Exception as ex:
        return jsonify({"status": False, "error":str(ex)})

def message_rank_down(self):
    client_id = request.args.get("client_id")
    discussion_id = request.args.get("id")
    try:
        new_rank = self.connections[client_id]["current_discussion"].message_rank_down(discussion_id)
        return jsonify({"status": True, "new_rank": new_rank})
    except Exception as ex:
        return jsonify({"status": False, "error":str(ex)})

def delete_message(self):
    client_id = request.args.get("client_id")
    discussion_id = request.args.get("id")
    if self.connections[client_id]["current_discussion"] is None:
        return jsonify({"status": False,"message":"No discussion is selected"})
    else:
        new_rank = self.connections[client_id]["current_discussion"].delete_message(discussion_id)
        ASCIIColors.yellow("Message deleted")
        return jsonify({"status":True,"new_rank": new_rank})