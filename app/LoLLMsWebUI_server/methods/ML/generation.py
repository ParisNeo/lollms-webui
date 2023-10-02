from flask import jsonify


def get_generation_status(self):
    return jsonify({"status":self.busy})

def stop_gen(self):
    self.cancel_gen = True
    return jsonify({"status": True})