import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from executions.core_execution import get_data_snapshot
from orchestrator import process_case_update

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def dashboard():
    return render_template(
        "index.html",
        case_name=os.getenv("CASE_NAME", "James Jolley Case Files"),
        owner=os.getenv("CASE_OWNER", "Matthew Jolley"),
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "system": "James Jolley Case Files Command Center",
        "framework": "DOE Automation Framework",
        "make_webhook_configured": bool(os.getenv("MAKE_WEBHOOK_URL", "").strip()),
    })


@app.route("/api/case-update", methods=["POST"])
def case_update():
    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({
            "status": "error",
            "message": "Invalid or missing JSON body.",
        }), 400

    result = process_case_update(payload)

    status_code = 200 if result.get("status") == "success" else 400
    return jsonify(result), status_code


@app.route("/api/snapshot", methods=["GET"])
def snapshot():
    return jsonify(get_data_snapshot())


@app.route("/api/test-payload", methods=["GET"])
def test_payload():
    return jsonify({
        "case_id": "JAMES-JOLLEY-CASE",
        "case_name": "James Jolley Case Files",
        "event_date": "2026-06-06",
        "event_time": "09:30",
        "location": "Portsmouth, Virginia",
        "category": "Timeline Event",
        "description": "Initial test update from the DOE Flask Command Center.",
        "summary": "Initial DOE test update.",
        "people_involved": ["Matthew Jolley"],
        "witness_names": [],
        "evidence_links": [],
        "phone_logs": [],
        "documents": [],
        "urgency_level": "medium",
        "follow_up_needed": True,
        "contradiction_check_needed": False,
        "source": "Flask Dashboard Test",
        "submitted_by": "Matthew Jolley",
    })


if __name__ == "__main__":
    app.run(debug=True)
