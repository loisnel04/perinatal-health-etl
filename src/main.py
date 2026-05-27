from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

from .fhir_export import export_fhir_bundles
from .load import initialize_database, load_rejected_records, load_valid_records
from .transform import load_mapping, parse_xml_file
from .validate import validate_record
from .validate_hl7 import validate_hl7_record
from .hl7_parser import parse_hl7_file


def run_pipeline(project_root: Path) -> None:
    """
    Run the perinatal ETL pipeline.

    The pipeline parses XML healthcare messages and includes a small HL7 v2
    parsing demo, validates records, stores valid/rejected data, and generates
    analytical outputs.
    """

    input_dir = project_root / "data" / "input_xml"
    hl7_dir = project_root / "data" / "input_hl7"
    processed_dir = project_root / "data" / "processed"
    rejected_dir = project_root / "data" / "rejected"
    output_dir = project_root / "output"

    db_path = output_dir / "perinatal_registry.db"
    schema_path = project_root / "sql" / "schema.sql"
    mapping_path = project_root / "config" / "mapping.yml"

    processed_dir.mkdir(parents=True, exist_ok=True)
    rejected_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    initialize_database(db_path, schema_path)
    mapping = load_mapping(mapping_path)

    xml_valid_records = []
    xml_rejected_records = []

    hl7_valide_records = []
    hl7_rejected_records = []

    # Process XML files in deterministic order for reproducible runs.
    for xml_file in sorted(input_dir.glob("*.xml")):
        try:
            record = parse_xml_file(xml_file, mapping)
            is_valid, errors = validate_record(record)

            if is_valid:
                xml_valid_records.append(record)
                shutil.copy2(xml_file, processed_dir / xml_file.name)
            else:
                xml_rejected_records.append({
                    "file_name": xml_file.name,
                    "message_id": record.get("message_id"),
                    "error_reason": "; ".join(errors),
                })
                shutil.copy2(xml_file, rejected_dir / xml_file.name)

        # Prevent one malformed XML message from stopping the full batch.
        except Exception as exc:
            xml_rejected_records.append({
                "file_name": xml_file.name,
                "message_id": None,
                "error_reason": f"XML parsing failure: {exc}",
            })
            shutil.copy2(xml_file, rejected_dir / xml_file.name)

    # Process a small HL7 v2 demo input using is own validation flow.
    for hl7_file in sorted(hl7_dir.glob("*.hl7")):
        try:
            record = parse_hl7_file(hl7_file)
            is_valid, errors = validate_hl7_record(record)

            if is_valid:
                print("HL7 record", record)
                hl7_valide_records.append(record)
                shutil.copy2(hl7_file, processed_dir / hl7_file.name)
            else:
                hl7_rejected_records.append({
                    "file_name": hl7_file.name,
                    "message_id": record.get("message_id"),
                    "error_reason": "; ".join(errors),
                })
                shutil.copy2(hl7_file, rejected_dir / hl7_file.name)

        # Keep the batch running even if one HL7 message is malformed.
        except Exception as exc:
            hl7_rejected_records.append({
                "file_name": hl7_file.name,
                "message_id": None,
                "error_reason": f"HL7 parsing failure: {exc}",
            })
            shutil.copy2(hl7_file, rejected_dir / hl7_file.name)

    load_valid_records(db_path, xml_valid_records)
    load_rejected_records(db_path, xml_rejected_records)

    if xml_valid_records:
        pd.DataFrame(xml_valid_records).to_csv(
            output_dir / "perinatal_records.csv",
            index=False,
        )

        export_fhir_bundles(
            xml_valid_records[:3],
            output_dir / "fhir_bundle_examples.json",
        )

    else:
        pd.DataFrame().to_csv(
            output_dir / "perinatal_records.csv",
            index=False,
        )

    pd.DataFrame(xml_rejected_records).to_csv(
        output_dir / "rejected_records.csv",
        index=False,
    )

    summary = {
        "xml_input_files": len(list(input_dir.glob("*.xml"))),
        "hl7_input_files": len(list(hl7_dir.glob("*.hl7"))),
        "valid_records": len(xml_valid_records),
        "rejected_records": len(xml_rejected_records),
        "database": str(db_path),
    }

    pd.DataFrame([summary]).to_csv(
        output_dir / "pipeline_summary.csv",
        index=False,
    )

    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run perinatal XML and HL7 ETL pipeline",
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )

    args = parser.parse_args()

    run_pipeline(args.project_root)