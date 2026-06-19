# DOE Automation Framework

DOE means:

D = Directives
O = Orchestration
E = Execution

Core rule:

Use LLMs for thinking.
Use deterministic code for doing.

## Directive

The James Jolley Case Files Command Center must track, organize, validate, route, and preserve all case information.

The system must handle:

- Evidence
- Witness statements
- Phone logs
- Detective updates
- Prosecutor updates
- Court updates
- Timeline events
- Contradictions
- Follow-up actions
- Document tracking
- Audit logs
- Error logs

## Orchestration

The Flask backend receives all case updates through `/api/case-update`.

The orchestrator performs:

1. Intake
2. Validation
3. Normalization
4. Categorization
5. Master case logging
6. Timeline updates
7. Evidence indexing
8. Witness logging
9. Phone log tracking
10. Official contact tracking
11. Court update tracking
12. Contradiction review
13. Follow-up creation
14. Case health scoring
15. Make.com webhook forwarding
16. Audit logging

## Execution

Python executes deterministic operations:

- Generate UUIDs
- Validate fields
- Normalize lists and booleans
- Save JSON safety records
- Sort timelines
- Create follow-up tasks
- Detect obvious contradictions
- Forward structured payloads to Make.com
- Return structured API responses

Make.com executes external workflow automation:

- Google Sheets storage
- Gmail alerts
- Error notifications
- Daily summaries
- Manual review queues
- Future OCR/transcription/OpenAI routes
