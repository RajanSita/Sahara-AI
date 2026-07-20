"""
priority_agent.py
Ranks tasks by urgency and dependency order.
Death certificate always first — it blocks almost everything else.
"""


PRIORITY_MAP = {
    # (institution_type, task_type_keyword): priority_rank
    "Obtain Death Certificate": 1,
    "Obtain Succession": 2,
    "Legal Heir Certificate": 2,
    "PF Death Benefit": 3,
    "Gratuity Claim": 4,
    "Final Settlement": 4,
    "Insurance Claim": 5,
    "Nominee Transfer": 6,
    "Account Closure": 6,
    "Safe Deposit Locker": 7,
    "Property Mutation": 8,
}


def _get_priority(task: dict) -> int:
    task_type = task.get("task_type", "")
    for keyword, rank in PRIORITY_MAP.items():
        if keyword.lower() in task_type.lower():
            return rank
    # Default by institution type
    type_defaults = {
        "government": 3,
        "employer": 4,
        "insurance": 5,
        "bank": 6,
        "property": 8,
    }
    return type_defaults.get(task.get("institution_type", ""), 99)


def _get_depends_on_labels(task: dict, all_tasks: list[dict]) -> list[str]:
    """
    Returns a list of task_type strings that this task depends on.
    Used for display and sequencing hints.
    """
    task_type = task.get("task_type", "")
    deps = []

    # Everything except the death cert itself depends on it
    if "Death Certificate" not in task_type:
        deps.append("Obtain Death Certificate")

    # Bank and insurance transfers need succession cert
    if any(kw in task_type for kw in ["Nominee Transfer", "Account Closure", "Insurance Claim", "Property Mutation"]):
        deps.append("Obtain Succession / Legal Heir Certificate")

    # Gratuity needs final settlement first
    if "Gratuity" in task_type:
        deps.append("Final Settlement & Dues Claim")

    return deps


def run(tasks: list[dict]) -> list[dict]:
    """
    Adds priority_rank and depends_on fields to each task.
    Returns sorted list (highest priority first).
    """
    import json

    for task in tasks:
        task["priority_rank"] = _get_priority(task)
        deps = _get_depends_on_labels(task, tasks)
        task["depends_on"] = json.dumps(deps)

    tasks.sort(key=lambda t: t["priority_rank"])
    return tasks
