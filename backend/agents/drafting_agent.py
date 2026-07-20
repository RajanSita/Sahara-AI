"""
drafting_agent.py
Generates ready-to-review letters and application drafts for each task.
Uses the LLM to produce institution-specific, formal, compassionate drafts.
"""
import json
import llm_client


SYSTEM_PROMPT = """You are a compassionate legal document assistant helping bereaved families in India 
complete administrative processes after the death of a loved one. 

Your job is to draft formal, accurate, and professionally worded letters or applications to institutions 
(banks, insurance companies, government offices, employers) on behalf of the family.

Guidelines:
- Use formal Indian English appropriate for official correspondence
- Be factual, respectful, and appropriately concise
- Always include: proper salutation, clear subject, body with all relevant details, closing
- Refer to the deceased with dignity (e.g. "Late Mr./Mrs. [Name]")
- Do NOT fabricate account numbers, policy numbers, or dates not provided
- Where specific details are missing, use [PLACEHOLDER] so the family can fill them in
- End with: Yours faithfully, [Primary Contact Name], [Relation to Deceased]
"""


def _build_prompt(task: dict, case_data: dict) -> str:
    deceased = case_data.get("deceased", {})
    contact = case_data.get("primary_contact") or {}
    docs = task.get("required_documents", "[]")
    if isinstance(docs, str):
        docs = json.loads(docs)

    return f"""Please draft a formal letter/application for the following:

TASK: {task['task_type']}
INSTITUTION: {task['institution_name']} ({task['institution_type']})

DECEASED PERSON DETAILS:
- Name: {deceased.get('name', '[Name]')}
- Date of Death: {deceased.get('date_of_death', '[Date]')}
- Place of Death: {deceased.get('place_of_death', '[Place]')}

PRIMARY CONTACT (APPLICANT):
- Name: {contact.get('name', '[Applicant Name]')}
- Relationship to Deceased: {contact.get('relation', '[Relation]')}
- Phone: {contact.get('phone', '[Phone]')}
- Email: {contact.get('email', '[Email]')}

DOCUMENTS TO BE ATTACHED (mention in the letter):
{chr(10).join(f'- {d}' for d in docs)}

Please produce:
1. SUBJECT LINE: (one line)
2. LETTER BODY: (complete formal letter)

Format your response exactly as:
SUBJECT: <subject line here>

<full letter body here>
"""


def run(task: dict, case_data: dict) -> dict:
    """
    Generate a draft for a single task.
    Returns dict with: subject, body, attachments
    """
    prompt = _build_prompt(task, case_data)

    raw = llm_client.complete(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.4,
        max_tokens=1500,
    )

    # Parse subject and body
    subject = ""
    body = raw

    if raw.startswith("SUBJECT:"):
        lines = raw.split("\n", 2)
        subject = lines[0].replace("SUBJECT:", "").strip()
        body = "\n".join(lines[1:]).strip()

    # Attachments from task
    docs = task.get("required_documents", "[]")
    if isinstance(docs, str):
        attachments = json.loads(docs)
    else:
        attachments = docs

    return {
        "subject": subject,
        "body": body,
        "attachments": json.dumps(attachments),
    }
