"""
main.py — Sahara.ai FastAPI Application
The core backend: routes, CORS, scheduler, and app lifecycle.
"""
import uuid
import json
import os
from typing import Optional
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import init_db, get_db, User, Case, Task, Draft, TaskStatus
from schemas import (
    IntakeFormRequest, CaseOut, TaskOut, DraftOut,
    DraftEditRequest, CreateCaseResponse
)
from auth import (
    UserOut, TokenResponse,
    create_access_token,
    get_current_user, get_optional_current_user
)
import agents.decision_agent as decision_agent
import gmail_service


# ── App Lifecycle ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("[OK] Sahara.ai backend started. Database initialised.")
    yield
    print("[--] Sahara.ai backend shutting down.")


app = FastAPI(
    title="Sahara.ai",
    description="AI-powered post-death estate administration assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow React dev server ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Sahara.ai", "version": "1.0.0"}


# ── Authentication (Google OAuth 2.0) ─────────────────────────────────────────

@app.get("/auth/google", tags=["Authentication"])
def google_auth_login():
    """Redirects user to Google OAuth consent screen for Gmail permissions."""
    auth_url = gmail_service.get_google_auth_url()
    return RedirectResponse(auth_url)


@app.get("/auth/google/callback", tags=["Authentication"])
def google_auth_callback(code: str, db: Session = Depends(get_db)):
    """Handles Google OAuth authorization code redirect, logs in user, and redirects to frontend."""
    try:
        res = gmail_service.exchange_code_for_user(code, db)
        user = res["user"]
        jwt_token = create_access_token({"sub": user.id})
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(f"{frontend_url}?token={jwt_token}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Authentication failed: {str(e)}")


@app.get("/auth/me", response_model=UserOut, tags=["Authentication"])
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


# ── Static Files (uploads) ────────────────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ── File Upload ───────────────────────────────────────────────────────────────

@app.post("/upload", tags=["Files"])
async def upload_file(file: UploadFile = File(...)):
    """Upload a document (death certificate, hospital doc, property doc, etc.)"""
    ext = os.path.splitext(file.filename or "file")[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join("uploads", safe_name)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    return {
        "filename": safe_name,
        "original_name": file.filename,
        "size": len(contents),
        "url": f"/uploads/{safe_name}",
    }


# ── Cases ─────────────────────────────────────────────────────────────────────

@app.post("/cases/", response_model=CreateCaseResponse, tags=["Cases"])
def create_case(form: IntakeFormRequest, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Submit intake form. Triggers the full agent pipeline:
    intake → classify → prioritise → draft.
    Returns the created case and number of tasks generated.
    """
    try:
        user_id = current_user.id if current_user else None
        db_case = decision_agent.process_new_case(form, db, user_id=user_id)
        task_count = db.query(Task).filter(Task.case_id == db_case.id).count()
        return CreateCaseResponse(
            case=CaseOut.model_validate(db_case),
            tasks_created=task_count,
            message=f"Case created successfully. {task_count} tasks identified and drafted.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.get("/cases/", tags=["Cases"])
def list_cases(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    """List cases (filtered by user if authenticated)."""
    query = db.query(Case)
    if current_user:
        query = query.filter((Case.user_id == current_user.id) | (Case.user_id.is_(None)))
    cases = query.order_by(Case.created_at.desc()).all()
    return [CaseOut.model_validate(c) for c in cases]


@app.get("/cases/{case_id}", response_model=CaseOut, tags=["Cases"])
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseOut.model_validate(case)


@app.delete("/cases/{case_id}", tags=["Cases"])
def delete_case(case_id: str, db: Session = Depends(get_db)):
    """Deletes a case and all its associated tasks and drafts."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"status": "success", "message": "Case deleted successfully"}


@app.get("/cases/{case_id}/tasks", response_model=list[TaskOut], tags=["Cases"])
def get_case_tasks(case_id: str, db: Session = Depends(get_db)):
    """Get all tasks for a case, ordered by priority."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    tasks = (
        db.query(Task)
        .filter(Task.case_id == case_id)
        .order_by(Task.priority_rank)
        .all()
    )
    return [TaskOut.model_validate(t) for t in tasks]


@app.get("/cases/{case_id}/stats", tags=["Cases"])
def get_case_stats(case_id: str, db: Session = Depends(get_db)):
    """Get task completion stats for a case."""
    tasks = db.query(Task).filter(Task.case_id == case_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Case not found or no tasks")
    
    stats = {
        "total": len(tasks),
        "not_started": sum(1 for t in tasks if t.status == TaskStatus.NOT_STARTED),
        "awaiting_approval": sum(1 for t in tasks if t.status == TaskStatus.AWAITING_APPROVAL),
        "sent": sum(1 for t in tasks if t.status == TaskStatus.SENT),
        "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
    }
    stats["progress_pct"] = round((stats["completed"] / stats["total"]) * 100)
    return stats


# ── Tasks ─────────────────────────────────────────────────────────────────────

@app.get("/tasks/{task_id}", response_model=TaskOut, tags=["Tasks"])
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut.model_validate(task)


@app.get("/tasks/{task_id}/draft", response_model=DraftOut, tags=["Tasks"])
def get_task_draft(task_id: str, db: Session = Depends(get_db)):
    """Get the current active draft for a task."""
    draft = db.query(Draft).filter(
        Draft.task_id == task_id,
        Draft.is_active == 1
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="No draft found for this task")
    return DraftOut.model_validate(draft)


@app.put("/tasks/{task_id}/approve", response_model=TaskOut, tags=["Tasks"])
def approve_task(task_id: str, db: Session = Depends(get_db)):
    """
    Approve a draft — marks task as SENT.
    In a real deployment this would also dispatch the email.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in [TaskStatus.AWAITING_APPROVAL, TaskStatus.NOT_STARTED]:
        raise HTTPException(status_code=400, detail=f"Task is in status '{task.status}' — cannot approve")
    
    task.status = TaskStatus.SENT
    task.sent_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@app.post("/tasks/{task_id}/send-gmail", tags=["Tasks"])
def send_gmail_task(task_id: str, recipient_email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Sends the drafted application directly from the logged-in user's personal @gmail.com account using Gmail API.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    draft = db.query(Draft).filter(Draft.task_id == task_id, Draft.is_active == 1).first()
    if not draft:
        raise HTTPException(status_code=404, detail="No active draft for this task")

    try:
        # Build list of relevant file attachments based on task type & uploaded documents
        attachments_to_send = []
        case = db.query(Case).filter(Case.id == task.case_id).first()
        if case and case.raw_intake:
            try:
                intake_data = json.loads(case.raw_intake)
                # Universal attachments for all authorities (Death Certificate & Hospital Summary)
                dc_file = intake_data.get("death_certificate_file")
                hs_file = intake_data.get("hospital_summary_file")
                if dc_file and os.path.exists(dc_file.lstrip("/")):
                    attachments_to_send.append(dc_file.lstrip("/"))
                if hs_file and os.path.exists(hs_file.lstrip("/")):
                    attachments_to_send.append(hs_file.lstrip("/"))

                # Authority-specific attachments (e.g. Property Documents for Property tasks)
                if task.institution_type == "property":
                    for p in intake_data.get("properties", []):
                        p_doc = p.get("document_file")
                        if p_doc and os.path.exists(p_doc.lstrip("/")):
                            attachments_to_send.append(p_doc.lstrip("/"))
            except Exception:
                pass

        res = gmail_service.send_via_gmail_api(
            user=current_user,
            recipient_email=recipient_email,
            subject=draft.subject or f"Application — {task.institution_name}",
            body=draft.body,
            attachments=attachments_to_send if attachments_to_send else None,
        )
        task.status = TaskStatus.SENT
        task.sent_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "status": "success",
            "result": res,
            "attachments_sent": [os.path.basename(a) for a in attachments_to_send],
            "task": TaskOut.model_validate(task),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/cases/{case_id}/sync-inbox", tags=["Cases"])
def sync_case_inbox(case_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Scans the user's Gmail inbox for incoming replies from institutions and updates task statuses.
    """
    try:
        res = gmail_service.sync_inbox_for_replies(current_user, db)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inbox sync failed: {str(e)}")


@app.put("/tasks/{task_id}/edit", response_model=DraftOut, tags=["Tasks"])
def edit_task_draft(task_id: str, edit: DraftEditRequest, db: Session = Depends(get_db)):
    """Edit the draft content."""
    draft = db.query(Draft).filter(
        Draft.task_id == task_id,
        Draft.is_active == 1
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="No active draft for this task")
    
    if edit.subject is not None:
        draft.subject = edit.subject
    draft.body = edit.body
    db.commit()
    db.refresh(draft)
    return DraftOut.model_validate(draft)


@app.put("/tasks/{task_id}/reject", response_model=TaskOut, tags=["Tasks"])
def reject_task(task_id: str, db: Session = Depends(get_db)):
    """Reject a draft — keeps task in awaiting_approval for re-review."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskStatus.AWAITING_APPROVAL
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@app.put("/tasks/{task_id}/complete", response_model=TaskOut, tags=["Tasks"])
def complete_task(task_id: str, db: Session = Depends(get_db)):
    """Mark a task as completed (family confirms institution has resolved it)."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@app.post("/tasks/{task_id}/followup", response_model=DraftOut, tags=["Tasks"])
def trigger_followup(task_id: str, db: Session = Depends(get_db)):
    """Manually trigger a follow-up draft for a sent task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != TaskStatus.SENT:
        raise HTTPException(status_code=400, detail="Task must be in SENT status to generate follow-up")
    
    try:
        new_draft = decision_agent.trigger_followup(task, db)
        if not new_draft:
            raise HTTPException(status_code=500, detail="Could not generate follow-up draft")
        return DraftOut.model_validate(new_draft)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
