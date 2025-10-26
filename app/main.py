from flask import Flask
from dotenv import load_dotenv
# Blueprints
from app.routes.web import web_bp
from app.routes.ask import ask_bp

import os

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.register_blueprint(web_bp)
    app.register_blueprint(ask_bp, url_prefix="/")

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
