import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data"
LOG_DIR = "logs"

MASTER_LOG = os.path.join(DATA_DIR, "master_case_log.json")
TIMELINE = os.path.join(DATA_DIR, "master_timeline.json")
EVIDENCE_INDEX = os.path.join(DATA_DIR, "evidence_index.json")
WITNESS_LOG = os.path.join(DATA_DIR, "witness_log.json")
PHONE_LOG = os.path.join(DATA_DIR, "phone_log.json")
OFFICIAL_CONTACTS = os.path.join(DATA_DIR, "official_contacts.json")
COURT_UPDATES = os.path.join(DATA_DIR, "court_updates.json")
CONTRADICTIONS = os.path.join(DATA_DIR, "contradictions.json")
FOLLOW_UPS = os.path.join(DATA_DIR, "follow_ups.json")
AUDIT_LOG = os.path.join(LOG_DIR, "audit_log.json")
ERROR_LOG = os.path.join(LOG_DIR, "error_log.json")
RAW_PAYLOADS = os.path.join(LOG_DIR, "raw_payloads.json")

REQUIRED_FIELDS = ["case_id", "category", "description"]

TIMELINE_CATEGORIES = {
    "Evidence",
    "Witness Statement",
    "Detective Update",
    "Prosecutor Update",
    "Court Update",
    "Timeline Event",
    "Phone Call",
    "Document Upload",
    "General Case Note",
}

VALID_CATEGORIES = {
    "Evidence",
    "Witness Statement",
    "Detective Update",
    "Prosecutor Update",
    "Court Update",
    "Timeline Event",
    "Phone Call",
    "Follow-Up Action",
    "Contradiction Review",
    "Document Upload",
    "General Case Note",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def load_json(path: str) -> List[Dict[str, Any]]:
    ensure_dirs()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_json(path: str, data: List[Dict[str, Any]]) -> None:
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def append_json(path: str, record: Dict[str, Any]) -> Dict[str, Any]:
    data = load_json(path)
    data.append(record)
    save_json(path, data)
    return record


def normalize_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if not value.strip():
            return []
        if "," in value:
            return [item.strip() for item in value.split(",") if item.strip()]
        return [value.strip()]
    return [value]


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "y"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def normalize_category(category: Any) -> str:
    if not category:
        return "General Case Note"

    raw = str(category).strip().lower()

    mapping = {
        "evidence": "Evidence",
        "witness": "Witness Statement",
        "witness statement": "Witness Statement",
        "detective": "Detective Update",
        "detective update": "Detective Update",
        "prosecutor": "Prosecutor Update",
        "prosecutor update": "Prosecutor Update",
        "court": "Court Update",
        "court update": "Court Update",
        "timeline": "Timeline Event",
        "timeline event": "Timeline Event",
        "phone": "Phone Call",
        "phone call": "Phone Call",
        "call": "Phone Call",
        "follow up": "Follow-Up Action",
        "follow-up": "Follow-Up Action",
        "follow-up action": "Follow-Up Action",
        "contradiction": "Contradiction Review",
        "contradiction review": "Contradiction Review",
        "document": "Document Upload",
        "document upload": "Document Upload",
        "general": "General Case Note",
        "note": "General Case Note",
        "general case note": "General Case Note",
    }

    normalized = mapping.get(raw, str(category).strip())

    if normalized not in VALID_CATEGORIES:
        return "General Case Note"

    return normalized


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if not payload.get(field)]
    return {
        "valid": len(missing) == 0,
        "missing_fields": missing,
    }


def save_raw_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "raw_payload_id": str(uuid.uuid4()),
        "received_at": utc_now(),
        "payload": payload,
    }
    return append_json(RAW_PAYLOADS, record)


def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    event_id = str(uuid.uuid4())
    now = utc_now()

    category = normalize_category(payload.get("category"))
    description = str(payload.get("description", "")).strip()
    summary = str(payload.get("summary") or description[:180]).strip()

    normalized = {
        "unique_event_id": event_id,
        "case_id": payload.get("case_id") or os.getenv("DEFAULT_CASE_ID", "JAMES-JOLLEY-CASE"),
        "case_name": payload.get("case_name") or os.getenv("CASE_NAME", "James Jolley Case Files"),
        "received_timestamp": now,
        "event_date": payload.get("event_date"),
        "event_time": payload.get("event_time"),
        "location": payload.get("location"),
        "category": category,
        "summary": summary,
        "description": description,
        "people_involved": normalize_list(payload.get("people_involved")),
        "witness_names": normalize_list(payload.get("witness_names")),
        "evidence_links": normalize_list(payload.get("evidence_links")),
        "phone_logs": normalize_list(payload.get("phone_logs")),
        "documents": normalize_list(payload.get("documents")),
        "urgency_level": str(payload.get("urgency_level") or "medium").strip().lower(),
        "follow_up_needed": normalize_bool(payload.get("follow_up_needed")),
        "contradiction_check_needed": normalize_bool(payload.get("contradiction_check_needed")),
        "source": payload.get("source") or "DOE Command Center",
        "submitted_by": payload.get("submitted_by") or os.getenv("CASE_OWNER", "Matthew Jolley"),
        "status": "logged",
        "raw_payload": payload,
    }

    if normalized["urgency_level"] not in {"low", "medium", "high"}:
        normalized["urgency_level"] = "medium"

    return normalized


def write_audit(module_name: str, action_taken: str, result: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    record = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": utc_now(),
        "module_name": module_name,
        "action_taken": action_taken,
        "result": result,
        "details": details or {},
    }
    return append_json(AUDIT_LOG, record)


def write_error(module_name: str, error_message: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    record = {
        "error_id": str(uuid.uuid4()),
        "timestamp": utc_now(),
        "module_name": module_name,
        "error_message": error_message,
        "payload": payload or {},
        "status": "unresolved",
    }
    append_json(ERROR_LOG, record)
    write_audit(module_name, "error_logged", "failed", record)
    return record


def save_master_case_log(record: Dict[str, Any]) -> Dict[str, Any]:
    return append_json(MASTER_LOG, record)


def update_master_timeline(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if record["category"] not in TIMELINE_CATEGORIES:
        return None

    timeline = load_json(TIMELINE)

    entry = {
        "timeline_id": str(uuid.uuid4()),
        "unique_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "case_name": record["case_name"],
        "event_date": record["event_date"],
        "event_time": record["event_time"],
        "location": record["location"],
        "category": record["category"],
        "timeline_summary": record["summary"],
        "people_involved": record["people_involved"],
        "witness_names": record["witness_names"],
        "source": record["source"],
        "created_at": utc_now(),
    }

    timeline.append(entry)

    timeline = sorted(
        timeline,
        key=lambda item: (
            str(item.get("event_date") or "9999-99-99"),
            str(item.get("event_time") or "99:99")
        )
    )

    save_json(TIMELINE, timeline)
    return entry


def create_evidence_index(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not record.get("evidence_links") and not record.get("documents") and record["category"] != "Evidence":
        return None

    evidence = {
        "evidence_id": str(uuid.uuid4()),
        "related_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "evidence_type": record["category"],
        "evidence_description": record["summary"],
        "evidence_links": record["evidence_links"],
        "documents": record["documents"],
        "source": record["source"],
        "witness_references": record["witness_names"],
        "upload_date": utc_now(),
        "status": "indexed",
    }

    return append_json(EVIDENCE_INDEX, evidence)


def create_witness_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not record.get("witness_names") and record["category"] != "Witness Statement":
        return None

    witness = {
        "witness_id": str(uuid.uuid4()),
        "related_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "witness_names": record["witness_names"],
        "statement_summary": record["summary"],
        "related_people": record["people_involved"],
        "related_evidence": record["evidence_links"],
        "date_logged": utc_now(),
        "follow_up_needed": record["follow_up_needed"],
        "status": "logged",
    }

    return append_json(WITNESS_LOG, witness)


def create_phone_log(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not record.get("phone_logs") and record["category"] != "Phone Call":
        return None

    phone = {
        "phone_log_id": str(uuid.uuid4()),
        "related_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "call_date": record["event_date"],
        "call_time": record["event_time"],
        "call_summary": record["summary"],
        "phone_logs": record["phone_logs"],
        "related_case_issue": record["category"],
        "follow_up_needed": record["follow_up_needed"],
        "status": "logged",
    }

    return append_json(PHONE_LOG, phone)


def create_official_contact(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if record["category"] not in {"Detective Update", "Prosecutor Update"}:
        return None

    contact = {
        "contact_event_id": str(uuid.uuid4()),
        "related_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "person_contacted": record["people_involved"],
        "agency_or_office": record["category"],
        "update_summary": record["summary"],
        "requested_follow_up": record["follow_up_needed"],
        "deadline": None,
        "status": "logged",
    }

    return append_json(OFFICIAL_CONTACTS, contact)


def create_court_update(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if record["category"] != "Court Update":
        return None

    court = {
        "court_event_id": str(uuid.uuid4()),
        "related_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "court_name": record["location"],
        "hearing_date": record["event_date"],
        "outcome": record["summary"],
        "notes": record["description"],
        "status": "logged",
    }

    return append_json(COURT_UPDATES, court)


def detect_possible_contradictions(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not record.get("contradiction_check_needed") and record["category"] != "Contradiction Review":
        return None

    prior_records = load_json(MASTER_LOG)
    conflicts = []

    for prior in prior_records:
        if prior.get("unique_event_id") == record["unique_event_id"]:
            continue

        same_date = prior.get("event_date") and prior.get("event_date") == record.get("event_date")
        different_location = same_date and prior.get("location") and record.get("location") and prior.get("location") != record.get("location")
        same_category = prior.get("category") == record.get("category")
        different_summary = same_category and prior.get("summary") and record.get("summary") and prior.get("summary") != record.get("summary")

        if different_location:
            conflicts.append({
                "conflicting_event_id": prior.get("unique_event_id"),
                "conflict_type": "same date different location",
                "prior_summary": prior.get("summary"),
            })

        if same_category and same_date and different_summary:
            conflicts.append({
                "conflicting_event_id": prior.get("unique_event_id"),
                "conflict_type": "same date/category different summary",
                "prior_summary": prior.get("summary"),
            })

    contradiction_detected = len(conflicts) > 0

    contradiction = {
        "contradiction_id": str(uuid.uuid4()),
        "related_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "contradiction_detected": contradiction_detected,
        "conflicts": conflicts,
        "conflict_summary": "Possible contradiction detected." if contradiction_detected else "No deterministic c        "confidence_score": 0.75 if contradiction_detected else 0.0,
        "recommended_follow_up": "Review related event records and verify dates, locations, and statements." if contradiction_detected else None,
        "urgency": "high" if contradiction_detected else "low",
        "status": "open" if contradiction_detected else "cleared",
        "created_at": utc_now(),
    }

    return append_json(CONTRADICTIONS, contradiction)


def create_follow_up(record: Dict[str, Any], contradiction: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    should_create = (
        record.get("follow_up_needed")
        or record.get("urgency_level") == "high"
        or record["category"] == "Contradiction Review"
        or bool(contradiction and contradiction.get("contradiction_detected"))
    )

    if not should_create:
        return None

    urgency = record.get("urgency_level", "medium")

    if contradiction and contradiction.get("contradiction_detected"):
        urgency = "high"

    days = 1 if urgency == "high" else 3 if urgency == "medium" else 7
    due_date = (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()

    follow_up = {
        "task_id": str(uuid.uuid4()),
        "related_event_id": record["unique_event_id"],
        "case_id": record["case_id"],
        "task_title": f"Follow up on {record['category']}",
        "recommended_action": contradiction.get("recommended_follow_up") if contradiction else f"Review and act on: {record['summary']}",
        "urgency_level": urgency,
        "assigned_to": os.getenv("CASE_OWNER", "Matthew Jolley"),
        "due_date": due_date,
        "status": "open",
        "created_at": utc_now(),
    }

    return append_json(FOLLOW_UPS, follow_up)


def calculate_case_health(record: Dict[str, Any], contradiction: Optional[Dict[str, Any]], follow_up: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    unresolved_contradictions = [
        item for item in load_json(CONTRADICTIONS)
        if item.get("status") == "open"
    ]

    open_followups = [
        item for item in load_json(FOLLOW_UPS)
        if item.get("status") == "open"
    ]

    if contradiction and contradiction.get("contradiction_detected"):
        status = "red"
        reason = "New contradiction detected."
    elif record.get("urgency_level") == "high":
        status = "red"
        reason = "High urgency case update."
    elif unresolved_contradictions:
        status = "red"
        reason = "Unresolved contradiction exists."
    elif follow_up or open_followups:
        status = "yellow"
        reason = "Follow-up action needed."
    else:
        status = "green"
        reason = "No urgent issue detected."

    return {
        "case_health_status": status,
        "reason": reason,
        "open_followups": len(open_followups),
        "unresolved_contradictions": len(unresolved_contradictions),
    }


def forward_to_make(payload: Dict[str, Any]) -> Dict[str, Any]:
    webhook_url = os.getenv("MAKE_WEBHOOK_URL", "").strip()

    if not webhook_url:
        return {
            "forwarded": False,
            "reason": "MAKE_WEBHOOK_URL is not configured.",
        }

    try:
        response = requests.post(webhook_url, json=payload, timeout=20)
        return {
            "forwarded": response.ok,
            "status_code": response.status_code,
            "response_text": response.text[:500],
        }
    except Exception as exc:
        write_error("make_forwarder", str(exc), payload)
        return {
            "forwarded": False,
            "reason": str(exc),
        }


def get_data_snapshot() -> Dict[str, Any]:
    return {
        "master_case_log": load_json(MASTER_LOG),
        "timeline": load_json(TIMELINE),
        "evidence_index": load_json(EVIDENCE_INDEX),
        "witness_log": load_json(WITNESS_LOG),
        "phone_log": load_json(PHONE_LOG),
        "official_contacts": load_json(OFFICIAL_CONTACTS),
        "court_updates": load_json(COURT_UPDATES),
        "contradictions": load_json(CONTRADICTIONS),
        "follow_ups": load_json(FOLLOW_UPS),
        "audit_log": load_json(AUDIT_LOG),
        "error_log": load_json(ERROR_LOG),
    }
