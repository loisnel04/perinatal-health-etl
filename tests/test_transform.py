from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from transform import load_mapping, parse_xml_file
from validate import validate_record
from load import initialize_database, load_valid_records


def test_valid_sample_record_parses_and_validates():
    mapping = load_mapping(PROJECT_ROOT / "config" / "mapping.yml")
    record = parse_xml_file(PROJECT_ROOT / "data" / "input_xml" / "birth_record_01.xml", mapping)

    assert record["message_id"] == "MSG001"
    assert record["mother_id"] == "M001"
    assert record["birth_weight_grams"] == 3420
    assert record["admission_nicu"] == 0

    is_valid, errors = validate_record(record)
    assert is_valid is True
    assert errors == []


def test_invalid_gestational_age_is_rejected():
    mapping = load_mapping(PROJECT_ROOT / "config" / "mapping.yml")
    record = parse_xml_file(PROJECT_ROOT / "data" / "input_xml" / "birth_record_06.xml", mapping)

    is_valid, errors = validate_record(record)
    assert is_valid is False
    assert any("gestational_age_weeks" in error for error in errors)    


def test_invalid_healthcare_values_are_rejected():
    record = {
        "message_id": "MSG_TEST",
        "mother_id": "M001",
        "child_id": "C001",
        "delivery_date": "2026-04-21",
        "gestational_age_weeks": 60,
        "birth_weight_grams": 12000,
        "apgar_5min": 9,
    }

    is_valid, errors = validate_record(record)

    assert is_valid is False
    assert any("gestational_age_weeks" in error.lower() for error in errors)
    assert any("birth_weight_grams" in error.lower() for error in errors)


def test_load_valid_records_can_be_rerun(tmp_path):
    db_path = tmp_path / "test.db"
    schema_path = Path("sql/schema.sql")

    initialize_database(db_path, schema_path)

    record = {
        "message_id": "MSG001",
        "source_system": "TEST",
        "message_timestamp": "2026-05-22T10:00:00",
        "mother_id": "M001",
        "mother_birth_date": "1992-04-12",
        "postal_code_prefix": "3511",
        "pregnancy_id": "P001",
        "gestational_age_weeks": 39,
        "gravida": 1,
        "parity": 0,
        "delivery_id": "D001",
        "delivery_date": "2026-04-21",
        "delivery_mode": "vaginal",
        "place_of_birth": "hospital",
        "child_id": "C001",
        "child_sex": "F",
        "birth_weight_grams": 3420,
        "apgar_5min": 9,
        "admission_nicu": 0,
    }

    load_valid_records(db_path, [record])
    load_valid_records(db_path, [record])