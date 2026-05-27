from pathlib import Path
from typing import Any, Dict


OBX_MAPPING = {
    "GESTATIONAL_AGE": "gestational_age_weeks",
    "BIRTH_WEIGHT": "birth_weight_grams",
    "DELIVERY_MODE": "delivery_mode",
    "CHILD_SEX": "child_sex",
    "APGAR_5MIN": "apgar_5min",
}


def parse_hl7_file(file_path: str | Path) -> Dict[str, Any]:
    """
    Parse a simple HL7 message and extract relevant fields into a dictionary.
    This is a very basic parser that looks for specific segments and fields.
    For a production system, consider using a robust HL7 parsing library like `hl7apy`
    """
    
    record: Dict[str, Any] = {
        "file_name": Path(file_path).name,
        "source_system": None,
        "message_id": None,
        "mother_id": None,
    }

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            fields = line.strip().split("|")

            if not fields:
                continue

            segment = fields[0]

            if segment == "MSH":
                record["source_system"] = fields[2] if len(fields) > 2 else None
                record["message_id"] = fields[9] if len(fields) > 9 else None

            elif segment == "PID":
                record["mother_id"] = fields[3] if len(fields) > 3 else None
                record["mother_birth_date"] = fields[7] if len(fields) > 7 else None

            elif segment == "OBX":
                observation_code = fields[3] if len(fields) > 3 else None
                observation_value = fields[5] if len(fields) > 5 else None

                mapped_field = OBX_MAPPING.get(observation_code)

                if mapped_field:
                    record[mapped_field] = observation_value

    for field in ["gestational_age_weeks", "birth_weight_grams", "apgar_5min"]:
        if record.get(field) is not None:
            record[field] = int(record[field])

    return record