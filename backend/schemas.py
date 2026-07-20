from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Intake Schemas ───────────────────────────────────────────────────────────

class BankAccount(BaseModel):
    bank_name: str
    account_type: str  # savings, current, joint, locker
    branch: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    has_nominee: Optional[bool] = None

class InsurancePolicy(BaseModel):
    insurer_name: str
    policy_type: str  # life, health, vehicle, other
    policy_number: Optional[str] = None
    nominee: Optional[str] = None

class EmployerInfo(BaseModel):
    employer_name: str
    designation: Optional[str] = None
    company_location: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    has_pf: Optional[bool] = True
    has_gratuity: Optional[bool] = True
    last_working_date: Optional[str] = None

class PropertyInfo(BaseModel):
    description: str  # "2BHK flat in Delhi", "agricultural land in UP"
    address: Optional[str] = None  # Full property address
    location: Optional[str] = None  # City/Region
    registration_number: Optional[str] = None
    google_maps_link: Optional[str] = None  # Optional
    document_file: Optional[str] = None  # Optional uploaded PDF filename

class FamilyMember(BaseModel):
    name: str
    relation: str  # spouse, son, daughter, parent, sibling
    is_primary_contact: bool = False
    phone: Optional[str] = None
    email: Optional[str] = None


class IntakeFormRequest(BaseModel):
    # Deceased
    deceased_name: str
    gender: Optional[str] = None  # male, female, other
    date_of_death: str  # ISO date string
    place_of_death: str  # REQUIRED — hospital, home address, etc.
    religion: Optional[str] = None

    # Financial
    banks: List[BankAccount] = []
    insurance_policies: List[InsurancePolicy] = []

    # Employment
    employers: List[EmployerInfo] = []

    # Property
    properties: List[PropertyInfo] = []

    # Family
    family_members: List[FamilyMember] = []

    # Death certificate
    death_certificate_obtained: bool = False
    death_certificate_file: Optional[str] = None  # filename if uploaded
    hospital_summary_file: Optional[str] = None  # hospital/cremation doc filename
    supporting_document_file: Optional[str] = None  # hospital/cremation doc filename


# ─── Case Schemas ─────────────────────────────────────────────────────────────

class CaseOut(BaseModel):
    id: str
    deceased_name: str
    date_of_death: str
    place_of_death: str
    religion: Optional[str]
    gender: Optional[str]
    family_contact_name: Optional[str]
    family_contact_relation: Optional[str]
    family_contact_phone: Optional[str]
    family_contact_email: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Task Schemas ─────────────────────────────────────────────────────────────

class TaskOut(BaseModel):
    id: str
    case_id: str
    institution_name: str
    institution_type: str
    task_type: str
    recipient_email: Optional[str] = None
    required_documents: Optional[str]
    priority_rank: int
    depends_on: Optional[str]
    status: str
    sent_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    status: Optional[str] = None


# ─── Draft Schemas ────────────────────────────────────────────────────────────

class DraftOut(BaseModel):
    id: str
    task_id: str
    subject: Optional[str]
    body: str
    attachments: Optional[str]
    version: int
    is_active: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DraftEditRequest(BaseModel):
    subject: Optional[str] = None
    body: str


# ─── Create Case Response ─────────────────────────────────────────────────────

class CreateCaseResponse(BaseModel):
    case: CaseOut
    tasks_created: int
    message: str
