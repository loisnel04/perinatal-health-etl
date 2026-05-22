from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

from .fhir_export import export_fhir_bundles
from .load import initialize_database, load_rejected_records, load_valid_records
from .transform import load_mapping, parse_xml_file
from .validate import validate_record


def run_pipeline(project_root: Path) -> None:
    """
    Run the perinatal XML ETL pipeline.

    The pipeline parses XML healthcare messages, validates records,
    stores valid/rejected data, and generates analytical outputs.
    """

    input_dir = project_root / "data" / "input_xml"
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

    valid_records = []
    rejected_records = []

    # Process XML files in deterministic order for reproducible runs.
    for xml_file in sorted(input_dir.glob("*.xml")):
        try:
            record = parse_xml_file(xml_file, mapping)
            is_valid, errors = validate_record(record)

            if is_valid:
                valid_records.append(record)
                shutil.copy2(xml_file, processed_dir / xml_file.name)
            else:
                rejected_records.append({
                    "file_name": xml_file.name,
                    "message_id": record.get("message_id"),
                    "error_reason": "; ".join(errors),
                })

                shutil.copy2(xml_file, rejected_dir / xml_file.name)

        # Prevent one malformed XML message from stopping the full batch.
        except Exception as exc:
            rejected_records.append({
                "file_name": xml_file.name,
                "message_id": None,
                "error_reason": f"Parsing failure: {exc}",
            })

            shutil.copy2(xml_file, rejected_dir / xml_file.name)

    load_valid_records(db_path, valid_records)
    load_rejected_records(db_path, rejected_records)

    if valid_records:
        pd.DataFrame(valid_records).to_csv(
            output_dir / "perinatal_records.csv",
            index=False,
        )

        export_fhir_bundles(
            valid_records[:3],
            output_dir / "fhir_bundle_examples.json",
        )

    else:
        pd.DataFrame().to_csv(
            output_dir / "perinatal_records.csv",
            index=False,
        )

    pd.DataFrame(rejected_records).to_csv(
        output_dir / "rejected_records.csv",
        index=False,
    )

    summary = {
        "input_files": len(list(input_dir.glob("*.xml"))),
        "valid_records": len(valid_records),
        "rejected_records": len(rejected_records),
        "database": str(db_path),
    }

    pd.DataFrame([summary]).to_csv(
        output_dir / "pipeline_summary.csv",
        index=False,
    )

    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run perinatal XML ETL pipeline",
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )

    args = parser.parse_args()

    run_pipeline(args.project_root)