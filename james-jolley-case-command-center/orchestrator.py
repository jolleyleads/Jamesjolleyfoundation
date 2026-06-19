from typing import Any, Dict

from executions.core_execution import (
    calculate_case_health,
    create_court_update,
    create_evidence_index,
    create_follow_up,
    create_official_contact,
    create_phone_log,
    create_witness_record,
    detect_possible_contradictions,
    forward_to_make,
    normalize_payload,
    save_master_case_log,
    save_raw_payload,
    update_master_timeline,
    validate_payload,
    write_audit,
    write_error,
)


def process_case_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        write_audit("orchestrator", "payload_received", "started", {"payload_preview": str(payload)[:500]})
        save_raw_payload(payload)

        validation = validate_payload(payload)

        if not validation["valid"]:
            error = {
                "status": "error",
                "message": "Missing required fields.",
                "missing_fields": validation["missing_fields"],
            }
            write_error("validation", "Missing required fields.", {"payload": payload, "validation": validation})
            return error

        clean = normalize_payload(payload)

        master_record = save_master_case_log(clean)
        timeline_record = update_master_timeline(clean)
        evidence_record = create_evidence_index(clean)
        witness_record = create_witness_record(clean)
        phone_record = create_phone_log(clean)
        official_contact_record = create_official_contact(clean)
        court_record = create_court_update(clean)
        contradiction_record = detect_possible_contradictions(clean)
        follow_up_record = create_follow_up(clean, contradiction_record)
        case_health = calculate_case_health(clean, contradiction_record, follow_up_record)

        make_payload = {
            "directive": "James Jolley case update logged and routed.",
            "orchestration": {
                "source": "Flask DOE Command Center",
                "destination": "Make.com / Google Sheets / Gmail",
            },
            "execution": {
                "master_record": master_record,
                "timeline_record": timeline_record,
                "evidence_record": evidence_record,
                "witness_record": witness_record,
                "phone_record": phone_record,
                "official_contact_record": official_contact_record,
                "court_record": court_record,
                "contradiction_record": contradiction_record,
                "follow_up_record": follow_up_record,
                "case_health": case_health,
            },
        }

        make_forward_result = forward_to_make(make_payload)

        write_audit(
            "orchestrator",
            "case_update_processed",
            "success",
            {
                "event_id": clean["unique_event_id"],
                "category": clean["category"],
                "case_health": case_health,
                "make_forward_result": make_forward_result,
            },
        )

        return {
            "status": "success",
            "message": "James Jolley case update logged successfully.",
            "case_id": clean["case_id"],
            "event_id": clean["unique_event_id"],
            "category": clean["category"],
            "case_health": case_health,
            "make_forward_result": make_forward_result,
            "records": {
                "master_record": master_record,
                "timeline_record": timeline_record,
                "evidence_record": evidence_record,
                "witness_record": witness_record,
                "phone_record": phone_record,
                "official_contact_record": official_contact_record,
                "court_record": court_record,
                "contradiction_record": contradiction_record,
                "follow_up_record": follow_up_record,
            },
        }

    except Exception as exc:
        write_error("orchestrator", str(exc), payload)
        return {
            "status": "error",
            "message": "Command center failed while processing update.",
            "error": str(exc),
        }
