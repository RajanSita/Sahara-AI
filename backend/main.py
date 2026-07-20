"""
main.py — Sahara.ai FastAPI Application
The core backend: routes, CORS, scheduler, and app lifecycle.
"""
import uuid
import json
import os
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import init_db, get_db, Case, Task, Draft, TaskStatus
from schemas import (
    IntakeFormRequest, CaseOut, TaskOut, DraftOut,
    DraftEditRequest, CreateCaseResponse
)
import agents.decision_agent as decision_agent


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


# ── Cases ─────────────────────────────────────────────────────────────────────

@app.post("/cases/", response_model=CreateCaseResponse, tags=["Cases"])
def create_case(form: IntakeFormRequest, db: Session = Depends(get_db)):
    """
    Submit intake form. Triggers the full agent pipeline:
    intake → classify → prioritise → draft.
    Returns the created case and number of tasks generated.
    """
    try:
        db_case = decision_agent.process_new_case(form, db)
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
def list_cases(db: Session = Depends(get_db)):
    """List all cases."""
    cases = db.query(Case).order_by(Case.created_at.desc()).all()
    return [CaseOut.model_validate(c) for c in cases]


@app.get("/cases/{case_id}", response_model=CaseOut, tags=["Cases"])
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseOut.model_validate(case)


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
