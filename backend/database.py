from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from datetime import datetime, timezone
import enum
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sahara.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class TaskStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    AWAITING_APPROVAL = "awaiting_approval"
    SENT = "sent"
    COMPLETED = "completed"
    REJECTED = "rejected"


class InstitutionType(str, enum.Enum):
    GOVERNMENT = "government"
    BANK = "bank"
    INSURANCE = "insurance"
    EMPLOYER = "employer"
    PROPERTY = "property"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    picture = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # Optional for Google OAuth users
    google_refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cases = relationship("Case", back_populates="user", cascade="all, delete-orphan")


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    deceased_name = Column(String, nullable=False)
    gender = Column(String)
    date_of_death = Column(String, nullable=False)
    place_of_death = Column(String, nullable=False)
    religion = Column(String)
    family_contact_name = Column(String)
    family_contact_relation = Column(String)
    family_contact_phone = Column(String)
    family_contact_email = Column(String)
    raw_intake = Column(Text)  # JSON of original form
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="cases")
    tasks = relationship("Task", back_populates="case", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    institution_name = Column(String, nullable=False)
    institution_type = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    recipient_email = Column(String, nullable=True)
    required_documents = Column(Text)  # JSON list
    priority_rank = Column(Integer, default=99)
    depends_on = Column(Text)  # JSON list of task IDs
    status = Column(String, default=TaskStatus.NOT_STARTED)
    sent_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="tasks")
    drafts = relationship("Draft", back_populates="task", cascade="all, delete-orphan")


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    subject = Column(String)
    body = Column(Text, nullable=False)
    attachments = Column(Text)  # JSON list
    version = Column(Integer, default=1)
    is_active = Column(Integer, default=1)  # 1 = current active draft
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task = relationship("Task", back_populates="drafts")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    # Ensure new columns exist in sqlite table
    with engine.connect() as conn:
        from sqlalchemy import text
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN picture VARCHAR"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN google_refresh_token TEXT"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE cases ADD COLUMN user_id VARCHAR"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE cases ADD COLUMN gender VARCHAR"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN recipient_email VARCHAR"))
            conn.commit()
        except Exception:
            pass
