"""
followup_agent.py
Monitors sent tasks and drafts polite follow-up communications
when institutions have not responded within the expected window.
"""
import json
import llm_client


FOLLOWUP_SYSTEM_PROMPT = """You are a compassionate administrative assistant helping a bereaved family 
follow up on pending requests submitted to institutions after a death in the family.

Write a polite, firm, and professional follow-up letter. The tone should be:
- Respectful and patient, but clear about the urgency
- Reference the original submission date
- Request a status update and expected resolution timeline
- Remain compassionate — remind the reader this is a grieving family

Format your response exactly as:
SUBJECT: <subject line>

<full follow-up letter body>
"""


def _build_followup_prompt(task: dict, original_draft: dict, case_data: dict, days_since_sent: int) -> str:
    deceased = case_data.get("deceased", {})
    contact = case_data.get("primary_contact") or {}

    return f"""Write a follow-up letter for a previously submitted request that has not received a response.

INSTITUTION: {task['institution_name']}
TASK: {task['task_type']}
ORIGINAL SUBJECT: {original_draft.get('subject', '[Original Subject]')}
DAYS SINCE SUBMISSION: {days_since_sent} days

DECEASED: Late {deceased.get('name', '[Name]')}, died on {deceased.get('date_of_death', '[Date]')}

APPLICANT:
- Name: {contact.get('name', '[Name]')}
- Relationship: {contact.get('relation', '[Relation]')}
- Phone: {contact.get('phone', '[Phone]')}

Please draft a polite follow-up letter requesting an update on this matter.
"""


def run(task: dict, original_draft: dict, case_data: dict, days_since_sent: int = 14) -> dict:
    """
    Generate a follow-up draft for a task that has been sent but not completed.
    Returns dict with: subject, body, attachments
    """
    prompt = _build_followup_prompt(task, original_draft, case_data, days_since_sent)

    raw = llm_client.complete(
        system_prompt=FOLLOWUP_SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.3,
        max_tokens=800,
    )

    subject = f"Follow-up: {original_draft.get('subject', task['task_type'])}"
    body = raw

    if raw.startswith("SUBJECT:"):
        lines = raw.split("\n", 2)
        subject = lines[0].replace("SUBJECT:", "").strip()
        body = "\n".join(lines[1:]).strip()

    return {
        "subject": subject,
        "body": body,
        "attachments": original_draft.get("attachments", "[]"),
    }
