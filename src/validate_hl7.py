from __future__ import annotations

from typing import Any, Dict, List, Tuple


REQUIRED_HL7_FIELDS = [
    "message_id",
    "mother_id",
    "gestational_age_weeks",
    "birth_weight_grams",
]

ALLOWED_DELIVERY_MODES = {
    "vaginal",
    "planned_caesarean",
    "emergency_caesarean",
    "assisted_vaginal",
}

ALLOWED_CHILD_SEX = {"M", "F", "U"}


def validate_hl7_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate one structured record extracted from an HL7 v2 message.

    HL7 demo messages may contain fewer fields than the XML records, so this
    validator focuses on the fields available in the HL7 input.

    Args:
        record: Structured record extracted from an HL7 v2 message.

    Returns:
        A tuple containing:
        - validation status as a boolean
        - list of validation error messages
    """

    errors: List[str] = []

    for field in REQUIRED_HL7_FIELDS:
        if record.get(field) in (None, ""):
            errors.append(f"Missing required HL7 field: {field}")

    ga = record.get("gestational_age_weeks")

    if ga is not None and not 22 <= ga <= 44:
        errors.append("gestational_age_weeks outside expected range 22-44")

    weight = record.get("birth_weight_grams")

    if weight is not None and not 300 <= weight <= 7000:
        errors.append("birth_weight_grams outside expected range 300-7000")

    apgar = record.get("apgar_5min")

    if apgar is not None and not 0 <= apgar <= 10:
        errors.append("apgar_5min outside expected range 0-10")

    delivery_mode = record.get("delivery_mode")

    if delivery_mode and delivery_mode not in ALLOWED_DELIVERY_MODES:
        errors.append(f"Unknown delivery_mode: {delivery_mode}")

    child_sex = record.get("child_sex")

    if child_sex and child_sex not in ALLOWED_CHILD_SEX:
        errors.append(f"Unknown child_sex: {child_sex}")

    return len(errors) == 0, errors