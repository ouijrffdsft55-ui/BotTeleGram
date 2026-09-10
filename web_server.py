import os
from flask import Flask

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return {
        "status": "running",
        "service": "Tu Tien Bot",
        "message": "🤖 Bot đang hoạt động"
    }


@web_app.route("/health")
def health():
    return "OK", 200


@web_app.route("/ping")
def ping():
    return "pong", 200


def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
