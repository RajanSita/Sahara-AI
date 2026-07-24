"""
decision_agent.py — The Orchestrator
Sequences all other agents to process a new case from intake to first drafts.
Also handles follow-up triggering for sent-but-unresolved tasks.
"""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Case, Task, Draft, TaskStatus
from schemas import IntakeFormRequest
import agents.intake_agent as intake_agent
import agents.classifier_agent as classifier_agent
import agents.priority_agent as priority_agent
import agents.drafting_agent as drafting_agent
import agents.followup_agent as followup_agent


def process_new_case(form_data: IntakeFormRequest, db: Session, user_id: str = None) -> Case:
    """
    Full pipeline for a new case:
    1. intake_agent → structured case data
    2. classifier_agent → task list
    3. priority_agent → ranked task list
    4. Persist Case + Tasks to DB
    5. drafting_agent → generate draft for each task
    6. Persist Drafts to DB
    Returns the created Case ORM object.
    """

    # ── Step 1: Intake ────────────────────────────────────────────────────────
    case_data = intake_agent.run(form_data)

    # ── Step 2: Classify ──────────────────────────────────────────────────────
    task_specs = classifier_agent.run(case_data)

    # ── Step 3: Prioritise ────────────────────────────────────────────────────
    ranked_tasks = priority_agent.run(task_specs)

    # ── Step 4: Persist Case ──────────────────────────────────────────────────
    contact = case_data.get("primary_contact") or {}
    case_id = str(uuid.uuid4())

    merged_intake = form_data.model_dump()
    merged_intake["death_certificate_file"] = getattr(form_data, "death_certificate_file", None)
    merged_intake["hospital_summary_file"] = getattr(form_data, "hospital_summary_file", None) or getattr(form_data, "supporting_document_file", None)
    merged_intake["supporting_document_file"] = getattr(form_data, "supporting_document_file", None) or getattr(form_data, "hospital_summary_file", None)

    db_case = Case(
        id=case_id,
        user_id=user_id,
        deceased_name=case_data["deceased"]["name"],
        gender=case_data["deceased"].get("gender"),
        date_of_death=case_data["deceased"]["date_of_death"],
        place_of_death=case_data["deceased"].get("place_of_death"),
        religion=case_data["deceased"].get("religion"),
        family_contact_name=contact.get("name"),
        family_contact_relation=contact.get("relation"),
        family_contact_phone=contact.get("phone"),
        family_contact_email=contact.get("email"),
        raw_intake=json.dumps(merged_intake, default=str),
    )
    db.add(db_case)
    db.flush()  # get ID without full commit

    # ── Step 5: Persist Tasks + Generate Drafts ───────────────────────────────
    for task_spec in ranked_tasks:
        task_id = str(uuid.uuid4())
        db_task = Task(
            id=task_id,
            case_id=case_id,
            institution_name=task_spec["institution_name"],
            institution_type=task_spec["institution_type"],
            task_type=task_spec["task_type"],
            recipient_email=task_spec.get("recipient_email"),
            required_documents=task_spec.get("required_documents"),
            priority_rank=task_spec.get("priority_rank", 99),
            depends_on=task_spec.get("depends_on"),
            status=TaskStatus.AWAITING_APPROVAL,
        )
        db.add(db_task)
        db.flush()

        # Generate draft
        try:
            draft_content = drafting_agent.run(task_spec, case_data)
            db_draft = Draft(
                id=str(uuid.uuid4()),
                task_id=task_id,
                subject=draft_content["subject"],
                body=draft_content["body"],
                attachments=draft_content["attachments"],
                version=1,
                is_active=1,
            )
            db.add(db_draft)
        except Exception as e:
            # If LLM fails, create placeholder draft
            db_draft = Draft(
                id=str(uuid.uuid4()),
                task_id=task_id,
                subject=f"Re: {task_spec['task_type']} — {task_spec['institution_name']}",
                body=f"[Draft generation failed: {str(e)}]\n\nPlease manually write a letter for:\nTask: {task_spec['task_type']}\nInstitution: {task_spec['institution_name']}",
                attachments=task_spec.get("required_documents", "[]"),
                version=1,
                is_active=1,
            )
            db.add(db_draft)

    db.commit()
    db.refresh(db_case)
    return db_case


def trigger_followup(task: Task, db: Session) -> Draft | None:
    """
    Generate a follow-up draft for a task that has been sent.
    Creates a new Draft version and sets task back to awaiting_approval.
    """
    # Get original draft
    original_draft = db.query(Draft).filter(
        Draft.task_id == task.id,
        Draft.is_active == 1
    ).first()

    if not original_draft:
        return None

    # Get case data for context
    case = db.query(Case).filter(Case.id == task.case_id).first()
    if not case:
        return None

    # Calculate days since sent
    days_since_sent = 14
    if task.sent_at:
        delta = datetime.now(timezone.utc) - task.sent_at.replace(tzinfo=timezone.utc)
        days_since_sent = delta.days

    # Build minimal case_data for the follow-up agent
    case_data = {
        "deceased": {
            "name": case.deceased_name,
            "date_of_death": case.date_of_death,
            "place_of_death": case.place_of_death,
        },
        "primary_contact": {
            "name": case.family_contact_name,
            "relation": case.family_contact_relation,
            "phone": case.family_contact_phone,
            "email": case.family_contact_email,
        },
    }

    task_dict = {
        "institution_name": task.institution_name,
        "institution_type": task.institution_type,
        "task_type": task.task_type,
    }

    original_dict = {
        "subject": original_draft.subject,
        "body": original_draft.body,
        "attachments": original_draft.attachments,
    }

    try:
        followup_content = followup_agent.run(task_dict, original_dict, case_data, days_since_sent)

        # Deactivate old draft
        original_draft.is_active = 0

        # Create new draft version
        new_version = (original_draft.version or 1) + 1
        new_draft = Draft(
            id=str(uuid.uuid4()),
            task_id=task.id,
            subject=followup_content["subject"],
            body=followup_content["body"],
            attachments=followup_content["attachments"],
            version=new_version,
            is_active=1,
        )
        db.add(new_draft)

        # Reset task to awaiting approval
        task.status = TaskStatus.AWAITING_APPROVAL

        db.commit()
        return new_draft

    except Exception as e:
        db.rollback()
        raise e
