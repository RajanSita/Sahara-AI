"""
intake_agent.py
Parses the family's raw form input into a normalised structured data object.
"""
import json
from schemas import IntakeFormRequest


def run(form_data: IntakeFormRequest) -> dict:
    """
    Convert the validated intake form into a structured case dictionary
    ready for the classifier and priority agents.
    Returns a plain dict (JSON-serialisable).
    """
    # Identify primary contact
    primary = next(
        (m for m in form_data.family_members if m.is_primary_contact),
        form_data.family_members[0] if form_data.family_members else None,
    )

    case_data = {
        "deceased": {
            "name": form_data.deceased_name,
            "gender": form_data.gender,
            "date_of_death": form_data.date_of_death,
            "place_of_death": form_data.place_of_death,
            "religion": form_data.religion,
        },
        "death_certificate_obtained": form_data.death_certificate_obtained,
        "death_certificate_file": form_data.death_certificate_file,
        "hospital_summary_file": form_data.hospital_summary_file,
        "banks": [b.model_dump() for b in form_data.banks],
        "insurance_policies": [p.model_dump() for p in form_data.insurance_policies],
        "employers": [e.model_dump() for e in form_data.employers],
        "properties": [p.model_dump() for p in form_data.properties],
        "family_members": [m.model_dump() for m in form_data.family_members],
        "primary_contact": primary.model_dump() if primary else None,
    }

    return case_data
