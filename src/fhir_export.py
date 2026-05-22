from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def record_to_fhir_bundle(record: Dict[str, Any]) -> Dict[str, Any]:
    """Create a simplified FHIR-like Bundle for portfolio demonstration.

    This is intentionally simplified and not a certified implementation of a national profile.
    It shows awareness of FHIR concepts: Bundle, Patient, Procedure, Observation.
    """
    
    mother_ref = f"Patient/mother-{record['mother_id']}"
    child_ref = f"Patient/child-{record['child_id']}"

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "identifier": {"value": record["message_id"]},
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": f"mother-{record['mother_id']}",
                    "birthDate": record.get("mother_birth_date"),
                    "address": [{"postalCode": record.get("postal_code_prefix")}],
                }
            },
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": f"child-{record['child_id']}",
                    "gender": {"M": "male", "F": "female", "U": "unknown"}.get(record.get("child_sex"), "unknown"),
                }
            },
            {
                "resource": {
                    "resourceType": "Procedure",
                    "id": f"delivery-{record.get('delivery_id')}",
                    "subject": {"reference": mother_ref},
                    "performedDateTime": record.get("delivery_date"),
                    "code": {"text": record.get("delivery_mode")},
                    "location": {"display": record.get("place_of_birth")},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": f"birthweight-{record['child_id']}",
                    "status": "final",
                    "subject": {"reference": child_ref},
                    "code": {"text": "Birth weight"},
                    "valueQuantity": {"value": record.get("birth_weight_grams"), "unit": "g"},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": f"gestational-age-{record['child_id']}",
                    "status": "final",
                    "subject": {"reference": child_ref},
                    "code": {"text": "Gestational age at birth"},
                    "valueQuantity": {"value": record.get("gestational_age_weeks"), "unit": "weeks"},
                }
            },
        ],
    }


def export_fhir_bundles(records: Iterable[Dict[str, Any]], output_path: str | Path) -> None:
    """
    Export structured records as simplified FHIR-style JSON bundles.
    """

    bundles: List[Dict[str, Any]] = [record_to_fhir_bundle(record) for record in records]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(bundles, file, indent=2)
