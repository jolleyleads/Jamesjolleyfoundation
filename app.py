from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>James Jolley Foundation</title>
<style>
body{margin:0;background:#0a1d2f;color:white;font-family:Arial}
header{padding:25px;background:#071522;border-bottom:4px solid #d4af37}
main{padding:60px;max-width:1000px;margin:auto}
h1{color:#d4af37;font-size:52px}
.card{background:#111f33;border:1px solid #d4af37;padding:25px;border-radius:12px;margin:20px 0}
.btn{background:#d4af37;color:#071522;padding:14px 24px;border-radius:8px;font-weight:bold;text-decoration:none;display:inline-block;margin:8px}
</style>
</head>
<body>
<header><strong>James Jolley Foundation</strong> — Turning Losses Into Lifelines</header>
<main>
<h1>Turning Losses Into Lifelines</h1>
<p>The James Jolley Foundation helps teenagers access addiction treatment immediately when insurance delays, Medicaid approval, or lack of funds stand in the way.</p>
<a class="btn" href="/health">Check System</a>
<a class="btn" href="mailto:Jolleyleads@gmail.com">Get Help</a>
<div class="card">
<h2>Why This Exists</h2>
<p>James Jolley was only 17 when he passed away from an accidental fentanyl overdose. He was scheduled to enter rehab just two days later, but Medicaid approval was still pending. That waiting period cost him his life.</p>
</div>
<div class="card">
<h2>DOE Command Center</h2>
<p><b>D:</b> Directives — Save lives, accept donations, capture help requests.</p>
<p><b>O:</b> Orchestration — Route families, donors, volunteers, partners, and media.</p>
<p><b>E:</b> Execution — Track, notify, automate, and follow up.</p>
</div>
</main>
</body>
</html>
"""

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "project": "James Jolley Foundation",
        "mission": "Turning Losses Into Lifelines",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/intake", methods=["POST"])
def intake():
    return jsonify({
        "success": True,
        "message": "James Jolley Foundation DOE intake endpoint is live."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
