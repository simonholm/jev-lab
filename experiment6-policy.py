"""Frozen Experiment 6 routing policy. Input is one Jev judgment object."""


def route(judgments):
    history = judgments["retain_for_history"]
    decision = judgments["explicit_decision"]
    change = judgments["completed_change"]
    missing_context = judgments["missing_required_context"]

    if history >= 0.8 and missing_context < 0.8 and (decision >= 0.8 or change >= 0.8):
        return "KEEP"
    if history >= 0.5 or decision >= 0.5 or change >= 0.5:
        return "DEEP_REVIEW"
    return "DROP"
