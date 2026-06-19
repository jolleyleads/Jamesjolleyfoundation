from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

DOE_SYSTEM = {
    "D": "Directives: Save lives, accept donations, capture help requests, organize outreach.",
    "O": "Orchestration: Route forms to donations, family help, partners, volunteers, media, and outreach.",
    "E": "Execution: Store data, notify admin, trigger Make.com, draft AI follow-ups, and track next actions."
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "project": "James Jolley Foundation",
        "mission": "Turning Losses Into Lifelines",
        "doe": DOE_SYSTEM,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/intake", methods=["POST"])
def intake():
    data = request.json or request.form.to_dict()
    record = {
        "received_at": datetime.utcnow().isoformat(),
        "type": data.get("type", "general"),
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "message": data.get("message"),
        "urgency": data.get("urgency", "normal"),
        "admin_email": "Jolleyleads@gmail.com",
        "status": "received"
    }
    return jsonify({
        "success": True,
        "message": "Request received by James Jolley Foundation DOE Command Center.",
        "data": record
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
