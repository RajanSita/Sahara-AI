"""
classifier_agent.py
Determines which institutional tasks are required based on the case data.
Returns a list of TaskSpec dicts.
"""
import json
from typing import Any


def run(case_data: dict) -> list[dict]:
    """
    Given structured case data, return a flat list of required tasks.
    Each task is a dict with: institution_name, institution_type, task_type, required_documents
    """
    tasks: list[dict] = []

    deceased = case_data["deceased"]
    name = deceased["name"]

    # ─── GOVERNMENT TASKS ────────────────────────────────────────────────────

    if not case_data.get("death_certificate_obtained"):
        tasks.append({
            "institution_name": "Municipal Corporation / Panchayat Office",
            "institution_type": "government",
            "task_type": "Obtain Death Certificate",
            "required_documents": json.dumps([
                "Hospital death summary / doctor's certificate",
                "Aadhaar card of deceased",
                "Aadhaar card of applicant",
                "Completed Form 2 (Death Registration)",
                "Proof of place of death (hospital records or address proof)",
            ]),
        })

    # Succession certificate — needed if any bank/property exists
    if case_data.get("banks") or case_data.get("properties"):
        tasks.append({
            "institution_name": "District Court",
            "institution_type": "government",
            "task_type": "Obtain Succession / Legal Heir Certificate",
            "required_documents": json.dumps([
                "Death certificate",
                "Proof of relationship (ration card, family register)",
                "Aadhaar cards of all legal heirs",
                "Affidavit listing all legal heirs",
                "Court fee stamp",
            ]),
        })

    # ─── BANK TASKS ──────────────────────────────────────────────────────────

    for bank in case_data.get("banks", []):
        bank_name = bank.get("bank_name", "Bank")
        account_type = bank.get("account_type", "savings")

        tasks.append({
            "institution_name": bank_name,
            "institution_type": "bank",
            "task_type": f"Nominee Transfer / Account Closure — {account_type.title()} Account",
            "required_documents": json.dumps([
                "Death certificate (attested copy)",
                "Succession certificate or legal heir certificate",
                "Aadhaar and PAN of nominee / legal heir",
                "Passbook or account statement",
                "Completed bank's nominee claim form",
                "Passport-size photograph of claimant",
            ]),
        })

        if account_type.lower() == "locker":
            tasks.append({
                "institution_name": bank_name,
                "institution_type": "bank",
                "task_type": "Safe Deposit Locker Access & Surrender",
                "required_documents": json.dumps([
                    "Death certificate",
                    "Succession certificate",
                    "Locker key (if available)",
                    "Identity proof of claimant",
                    "Bank's locker nomination / claim form",
                ]),
            })

    # ─── INSURANCE TASKS ─────────────────────────────────────────────────────

    for policy in case_data.get("insurance_policies", []):
        insurer = policy.get("insurer_name", "Insurance Company")
        policy_type = policy.get("policy_type", "life")

        tasks.append({
            "institution_name": insurer,
            "institution_type": "insurance",
            "task_type": f"{policy_type.title()} Insurance Claim — Death Claim",
            "required_documents": json.dumps([
                "Original policy document",
                "Death certificate (attested)",
                "Claimant's identity proof (Aadhaar + PAN)",
                "NEFT / bank details of claimant for payout",
                "Completed insurer's death claim form",
                "Medical records / cause of death certificate (if required)",
            ]),
        })

    # ─── EMPLOYER TASKS ──────────────────────────────────────────────────────

    for employer in case_data.get("employers", []):
        emp_name = employer.get("employer_name", "Employer")

        tasks.append({
            "institution_name": emp_name,
            "institution_type": "employer",
            "task_type": "Final Settlement & Dues Claim",
            "required_documents": json.dumps([
                "Death certificate",
                "Employee ID / appointment letter",
                "Bank details of claimant",
                "Legal heir / succession certificate",
                "Completed employer HR claim form",
            ]),
        })

        if employer.get("has_pf"):
            tasks.append({
                "institution_name": "EPFO (Employees' Provident Fund Organisation)",
                "institution_type": "government",
                "task_type": "PF Death Benefit Claim (Form 20 + Form 10D)",
                "required_documents": json.dumps([
                    "Death certificate",
                    "UAN of deceased",
                    "Nominee's Aadhaar and PAN",
                    "Bank account of nominee (linked to Aadhaar)",
                    "Completed Form 20 (PF withdrawal) and Form 10D (pension)",
                ]),
            })

        if employer.get("has_gratuity"):
            tasks.append({
                "institution_name": emp_name,
                "institution_type": "employer",
                "task_type": "Gratuity Claim (Form I — Nominee Claim)",
                "required_documents": json.dumps([
                    "Death certificate",
                    "Service record / appointment letter",
                    "Nominee declaration form (Form F)",
                    "Legal heir certificate",
                    "Bank details for payment",
                ]),
            })

    # ─── PROPERTY TASKS ──────────────────────────────────────────────────────

    for prop in case_data.get("properties", []):
        desc = prop.get("description", "Property")

        tasks.append({
            "institution_name": "Local Revenue / Municipal Authority",
            "institution_type": "property",
            "task_type": f"Property Mutation — {desc}",
            "required_documents": json.dumps([
                "Death certificate",
                "Succession / legal heir certificate",
                "Original property documents (sale deed / title deed)",
                "Latest property tax receipt",
                "Identity proof of all heirs",
                "Mutation application form",
            ]),
        })

    return tasks
