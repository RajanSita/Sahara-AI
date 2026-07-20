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

CRITICAL INSTRUCTIONS ON PLACEHOLDERS:
- NEVER output literal text like "[PLACEHOLDER]", "[PRIMARY CONTACT NAME]", "[City, State, Pincode]", "[Phone]", "[Email]", "[Address]".
- ALWAYS populate the letter using the real applicant name, deceased name, relationship, dates, phone, email, bank details, and property addresses provided in the prompt context.
- For the recipient address block at the top, generate a formal official designation and address based on the institution (e.g. "To The Municipal Commissioner / Local Registrar of Births & Deaths", "To The Branch Manager, State Bank of India").
- Refer to the deceased with dignity (e.g. "Late Mr. [Name]" or "Late Mrs. [Name]" based on gender).
- End with: "Yours faithfully, <Applicant Real Name>, <Relationship to Deceased>".
"""


def _build_prompt(task: dict, case_data: dict) -> str:
    deceased = case_data.get("deceased", {})
    contact = case_data.get("primary_contact") or {}
    docs = task.get("required_documents", "[]")
    if isinstance(docs, str):
        docs = json.loads(docs)

    gender_title = "Mrs." if deceased.get("gender", "").lower() == "female" else "Mr."
    dec_name = deceased.get('name', 'Deceased')
    dec_full = f"Late {gender_title} {dec_name}" if not dec_name.startswith("Late") else dec_name

    rel = contact.get('relation') or contact.get('relationship') or 'Family Member'
    applicant_name = contact.get('name') or 'Applicant'
    applicant_phone = contact.get('phone') or 'Not provided'
    applicant_email = contact.get('email') or 'Not provided'

    # Match specific asset details if task relates to property/bank/employer/insurance
    inst_name = task.get("institution_name", "")
    inst_type = task.get("institution_type", "")
    
    asset_details = []
    if inst_type == "bank":
        for b in case_data.get("banks", []):
            if b.get("bank_name", "").lower() in inst_name.lower() or inst_name.lower() in b.get("bank_name", "").lower():
                if b.get("account_number"): asset_details.append(f"Account Number: {b['account_number']}")
                if b.get("ifsc_code"): asset_details.append(f"IFSC Code: {b['ifsc_code']}")
                if b.get("branch_name"): asset_details.append(f"Branch: {b['branch_name']}")
    elif inst_type == "property":
        for p in case_data.get("properties", []):
            if p.get("property_address"): asset_details.append(f"Property Address: {p['property_address']}")
            if p.get("property_type"): asset_details.append(f"Property Type: {p['property_type']}")
            if p.get("google_maps_link"): asset_details.append(f"Location Link: {p['google_maps_link']}")
    elif inst_type == "employer":
        for e in case_data.get("employers", []):
            if e.get("company_name", "").lower() in inst_name.lower() or inst_name.lower() in e.get("company_name", "").lower():
                if e.get("employee_id"): asset_details.append(f"Employee ID: {e['employee_id']}")
                if e.get("department"): asset_details.append(f"Department: {e['department']}")
                if e.get("company_location"): asset_details.append(f"Office Location: {e['company_location']}")
    elif inst_type == "insurance":
        for p in case_data.get("insurance_policies", []):
            if p.get("company_name", "").lower() in inst_name.lower() or inst_name.lower() in p.get("company_name", "").lower():
                if p.get("policy_number"): asset_details.append(f"Policy Number: {p['policy_number']}")
                if p.get("sum_assured"): asset_details.append(f"Sum Assured: ₹{p['sum_assured']}")

    asset_info_str = "\n".join(f"- {a}" for a in asset_details) if asset_details else "None specified"

    return f"""Please draft a complete, formal letter/application for:

TASK: {task['task_type']}
INSTITUTION: {inst_name} ({inst_type})

DECEASED DETAILS:
- Full Name: {dec_full}
- Date of Death: {deceased.get('date_of_death', '')}
- Place of Death: {deceased.get('place_of_death', '')}

APPLICANT DETAILS (Use these directly in letter):
- Applicant Name: {applicant_name}
- Relationship: {rel} of {dec_full}
- Phone: {applicant_phone}
- Email: {applicant_email}

ASSET / INSTITUTION SPECIFIC DATA:
{asset_info_str}

REQUIRED ATTACHMENTS:
{chr(10).join(f'- {d}' for d in docs)}

IMPORTANT: Do NOT output [PLACEHOLDER] or [PRIMARY CONTACT NAME]. Write a complete, ready-to-send letter.

Format:
SUBJECT: <subject line>

<letter body>
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
        temperature=0.3,
        max_tokens=1500,
    )

    # Parse subject and body
    subject = ""
    body = raw

    if raw.startswith("SUBJECT:"):
        lines = raw.split("\n", 2)
        subject = lines[0].replace("SUBJECT:", "").strip()
        body = "\n".join(lines[1:]).strip()

    # Post-processing string cleanup fallback
    contact = case_data.get("primary_contact") or {}
    applicant_name = contact.get('name') or 'Applicant'
    applicant_rel = contact.get('relation') or contact.get('relationship') or 'Family Member'
    applicant_phone = contact.get('phone') or ''
    applicant_email = contact.get('email') or ''

    body = body.replace("[PRIMARY CONTACT NAME]", applicant_name)
    body = body.replace("[Primary Contact Name]", applicant_name)
    body = body.replace("[APPLICANT NAME]", applicant_name)
    body = body.replace("[Applicant Name]", applicant_name)
    body = body.replace("[Relation to Deceased]", applicant_rel)
    body = body.replace("[Relationship]", applicant_rel)
    body = body.replace("[PHONE]", applicant_phone)
    body = body.replace("[Phone]", applicant_phone)
    body = body.replace("[EMAIL]", applicant_email)
    body = body.replace("[Email]", applicant_email)
    body = body.replace("[PLACEHOLDER]", "N/A")

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
