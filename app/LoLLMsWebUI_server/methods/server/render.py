from flask import render_template


def main(self):
        return render_template("main.html")
    
def settings(self):
    return render_template("settings.html")

def help(self):
    return render_template("help.html")

def training(self):
    return render_template("training.html")

def extensions(self):
    return render_template("extensions.html")

def index(self):
    return render_template("index.html")