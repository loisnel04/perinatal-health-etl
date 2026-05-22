from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict

import yaml


def _text(root: ET.Element, path: str) -> str | None:
    node = root.find(path)
    if node is None or node.text is None:
        return None
    value = node.text.strip()
    return value if value != "" else None


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _to_bool_int(value: str | None) -> int | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return 1
    if normalized in {"false", "0", "no", "n"}:
        return 0
    return None


def load_mapping(mapping_path: str | Path) -> Dict[str, str]:
    with open(mapping_path, "r", encoding="utf-8") as file:
        mapping = yaml.safe_load(file)
    return mapping["fields"]


def parse_xml_file(xml_path: str | Path, mapping: Dict[str, str]) -> Dict[str, Any]:
    root = ET.parse(xml_path).getroot()
    record: Dict[str, Any] = {field: _text(root, xpath) for field, xpath in mapping.items()}

    for field in ["gestational_age_weeks", "gravida", "parity", "birth_weight_grams", "apgar_5min"]:
        record[field] = _to_int(record.get(field))

    record["admission_nicu"] = _to_bool_int(record.get("admission_nicu"))
    record["file_name"] = Path(xml_path).name
    return record
