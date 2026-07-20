"""
classifier_agent.py
Determines which institutional tasks are required based on the case data.
Returns a list of TaskSpec dicts.
"""
import json
from typing import Any


TESTING_MODE = True
TESTING_EMAIL = "sahara.ai.team@gmail.com"


def _guess_recipient_email(inst_name: str, inst_type: str) -> str:
    if TESTING_MODE:
        return TESTING_EMAIL

    name_lower = inst_name.lower().strip()

    # ─── BANKS (Public, Private, RRBs, Payments Banks) ────────────────────────
    # if "sbi" in name_lower or "state bank" in name_lower:
    #     return "customercare@sbi.co.in"
    # elif "hdfc" in name_lower and ("life" not in name_lower and "ergo" not in name_lower):
    #     return "support@hdfcbank.com"
    # elif "icici" in name_lower and ("pru" not in name_lower and "lombard" not in name_lower):
    #     return "care@icicibank.com"
    # elif "axis" in name_lower:
    #     return "nodal.officer@axisbank.com"
    # elif "punjab national" in name_lower or "pnb" in name_lower and "metlife" not in name_lower:
    #     return "care@pnb.co.in"
    # elif "bank of baroda" in name_lower or "bob" in name_lower:
    #     return "customercare@bankofbaroda.com"
    # elif "canara" in name_lower and "hsbc" not in name_lower:
    #     return "customerfirst@canarabank.com"
    # elif "union bank" in name_lower:
    #     return "customercare@unionbankofindia.bank"
    # elif "bank of india" in name_lower or "boi" in name_lower:
    #     return "boi.starconnect@bankofindia.co.in"
    # elif "indian bank" in name_lower:
    #     return "customercomplaints@indianbank.co.in"
    # elif "central bank" in name_lower:
    #     return "complaints@centralbank.co.in"
    # elif "indian overseas" in name_lower or "iob" in name_lower:
    #     return "dgmcustomer@iob.in"
    # elif "uco bank" in name_lower:
    #     return "uco.custcare@ucobank.co.in"
    # elif "punjab & sind" in name_lower or "psb" in name_lower:
    #     return "hodits@psb.co.in"
    # elif "kotak" in name_lower and "life" not in name_lower:
    #     return "service.bank@kotak.com"
    # elif "indusind" in name_lower:
    #     return "reachus@indusind.com"
    # elif "yes bank" in name_lower:
    #     return "yestouch@yesbank.in"
    # elif "idbi" in name_lower:
    #     return "customercare@idbi.co.in"
    # elif "federal bank" in name_lower:
    #     return "contact@federalbank.co.in"
    # elif "idfc" in name_lower:
    #     return "banker@idfcfirstbank.com"
    # elif "bandhan" in name_lower:
    #     return "customercare@bandhanbank.com"
    # elif "rbl" in name_lower or "ratnakar" in name_lower:
    #     return "customercare@rblbank.com"
    # elif "kvb" in name_lower or "karur" in name_lower:
    #     return "customerservice@kvbmail.com"
    # elif "south indian" in name_lower or "sib" in name_lower:
    #     return "customercare@sib.co.in"
    # elif "city union" in name_lower or "cub" in name_lower:
    #     return "customercare@cityunionbank.in"
    # elif "jammu" in name_lower or "j&k" in name_lower or "jkb" in name_lower:
    #     return "helpdesk@jkbmail.com"
    # elif "dhanlaxmi" in name_lower or "dhanbank" in name_lower:
    #     return "customercare@dhanbank.co.in"
    # elif "au small" in name_lower or "au bank" in name_lower:
    #     return "customercare@aubank.in"
    # elif "equitas" in name_lower:
    #     return "services@equitasbank.com"
    # elif "ujjivan" in name_lower:
    #     return "customercare@ujjivan.com"
    # elif "paytm" in name_lower:
    #     return "care@paytmbank.com"
    # elif "post office" in name_lower or "ippb" in name_lower or "india post" in name_lower:
    #     return "contact@ippbonline.in"

    # ─── INSURANCE (Life, Health, General) ────────────────────────────────────
    # elif "lic" in name_lower or "life insurance corporation" in name_lower:
    #     return "claims@licindia.com"
    # elif "hdfc life" in name_lower:
    #     return "service@hdfclife.com"
    # elif "sbi life" in name_lower:
    #     return "info@sbilife.co.in"
    # elif "icici pru" in name_lower or "icici prudential" in name_lower:
    #     return "lifeline@iciciprulife.com"
    # elif "max life" in name_lower:
    #     return "service.helpdesk@maxlifeinsurance.com"
    # elif "bajaj allianz life" in name_lower:
    #     return "customercare@bajajallianz.co.in"
    # elif "tata aia" in name_lower:
    #     return "customercare@tataaia.com"
    # elif "kotak life" in name_lower:
    #     return "clientservicing@kotak.com"
    # elif "aditya birla" in name_lower or "birla sun" in name_lower:
    #     return "care.lifeinsurance@adityabirlacapital.com"
    # elif "pnb metlife" in name_lower or "metlife" in name_lower:
    #     return "indiaservice@pnbmetlife.co.in"
    # elif "sud life" in name_lower or "star union" in name_lower:
    #     return "customercare@sudlife.in"
    # elif "reliance nippon" in name_lower or "reliance life" in name_lower:
    #     return "rnlife.customerservice@relianceada.com"
    # elif "canara hsbc" in name_lower:
    #     return "customercare@canarahsbclife.in"
    # elif "indiafirst" in name_lower:
    #     return "customer.first@indiafirstlife.com"
    # elif "edelweiss tokio" in name_lower:
    #     return "care@edelweisstokio.in"
    # elif "future generali" in name_lower:
    #     return "care@futuregenerali.in"
    # elif "ageas federal" in name_lower or "idbi federal" in name_lower:
    #     return "support@ageasfederal.com"
    # elif "pramerica" in name_lower:
    #     return "contactus@pramericalife.in"
    # elif "aviva" in name_lower:
    #     return "care@avivaindia.com"
    # elif "sahara life" in name_lower:
    #     return "customer.support@saharalife.com"
    # elif "star health" in name_lower:
    #     return "support@starhealth.in"
    # elif "care health" in name_lower or "religare health" in name_lower:
    #     return "customerfirst@careinsurance.com"
    # elif "niva bupa" in name_lower or "max bupa" in name_lower:
    #     return "customercare@nivabupa.com"
    # elif "new india assurance" in name_lower:
    #     return "tech.support@newindia.co.in"
    # elif "united india" in name_lower:
    #     return "customercare@uiic.co.in"
    # elif "national insurance" in name_lower:
    #     return "customer.relation@nic.co.in"
    # elif "oriental insurance" in name_lower:
    #     return "cs@orientalinsurance.co.in"
    # elif "icici lombard" in name_lower:
    #     return "customersupport@icicilombard.com"
    # elif "hdfc ergo" in name_lower:
    #     return "care@hdfcergo.com"
    # elif "bajaj allianz general" in name_lower or "bagic" in name_lower:
    #     return "bagichelp@bajajallianz.co.in"
    # elif "tata aig" in name_lower:
    #     return "customersupport@tataaig.com"
    # elif "sbi general" in name_lower:
    #     return "customer.care@sbigeneral.in"
    # elif "reliance general" in name_lower:
    #     return "services.rgicl@relianceada.com"
    # elif "iffco tokio" in name_lower:
    #     return "websupport@iffcotokio.co.in"
    # elif "cholamandalam" in name_lower or "chola ms" in name_lower:
    #     return "customercare@cholams.murugappa.com"
    # elif "royal sundaram" in name_lower:
    #     return "customer.services@royalsundaram.in"
    # elif "liberty general" in name_lower or "liberty insurance" in name_lower:
    #     return "care@libertyinsurance.in"
    # elif "universal sompo" in name_lower:
    #     return "contactus@universalsompo.com"
    # elif "manipal cigna" in name_lower or "manipalcigna" in name_lower:
    #     return "customercare@manipalcigna.com"
    # elif "digit" in name_lower or "go digit" in name_lower:
    #     return "hello@godigit.com"
    # elif "acko" in name_lower:
    #     return "hello@acko.com"

    # ─── GOVERNMENT & OTHER AUTHORITIES ───────────────────────────────────────
    # elif "epfo" in name_lower or "provident fund" in name_lower:
    #     return "commissioner@epfindia.gov.in"
    # elif "municipal" in name_lower or "panchayat" in name_lower or "corporation" in name_lower:
    #     return "registrar.birthdeath@delhi.gov.in"
    # elif "court" in name_lower or "legal heir" in name_lower:
    #     return "filing.districtcourt@indiancourts.gov.in"

    clean_domain = name_lower.replace("bank", "").replace("life", "").replace("insurance", "").replace("limited", "").replace("ltd", "").replace(" ", "").replace("&", "")
    if inst_type == "employer":
        return f"hr@{clean_domain}.com"
    elif inst_type == "insurance":
        return f"claims@{clean_domain}.com"
    elif inst_type == "bank":
        return f"customercare@{clean_domain}.com"
    return f"info@{clean_domain}.gov.in" if inst_type == "government" else f"contact@{clean_domain}.com"


def run(case_data: dict) -> list[dict]:
    """
    Given structured case data, return a flat list of required tasks.
    Each task is a dict with: institution_name, institution_type, task_type, required_documents, recipient_email
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
            "recipient_email": _guess_recipient_email("Municipal Corporation / Panchayat Office", "government"),
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
            "recipient_email": _guess_recipient_email("District Court", "government"),
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
            "recipient_email": _guess_recipient_email(bank_name, "bank"),
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
                "recipient_email": _guess_recipient_email(bank_name, "bank"),
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
            "recipient_email": _guess_recipient_email(insurer, "insurance"),
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
            "recipient_email": _guess_recipient_email(emp_name, "employer"),
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
                "recipient_email": "commissioner@epfindia.gov.in",
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
                "recipient_email": _guess_recipient_email(emp_name, "employer"),
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
            "recipient_email": "revenue.mutation@municipal.gov.in",
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
