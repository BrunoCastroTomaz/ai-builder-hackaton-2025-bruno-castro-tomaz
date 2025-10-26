#app/routes/web.py 

from flask import Blueprint, render_template, redirect

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def index():
    return redirect("/chat")

@web_bp.route("/chat")
def chat():
    return render_template("chat.html")
