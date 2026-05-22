from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict

import yaml


def _text(root: ET.Element, path: str) -> str | None:
    """
    Extract and clean text from an XML element path.

    Args:
        root: Root XML element.
        path: XPath-like element path.

    Returns:
        Cleaned text value or None if the element is missing/empty.
    """

    node = root.find(path)

    if node is None or node.text is None:
        return None

    value = node.text.strip()

    return value if value != "" else None


def _to_int(value: str | None) -> int | None:
    """
    Safely convert a string value to an integer.

    Args:
        value: Input string value.

    Returns:
        Integer value or None if conversion fails.
    """

    if value is None:
        return None

    try:
        return int(value)

    except ValueError:
        return None


def _to_bool_int(value: str | None) -> int | None:
    """
    Convert common boolean-like values into integer flags.

    Accepted true values:
    true, 1, yes, y

    Accepted false values:
    false, 0, no, n

    Args:
        value: Input string value.

    Returns:
        1 for true values, 0 for false values, or None if invalid.
    """

    if value is None:
        return None

    normalized = value.strip().lower()

    if normalized in {"true", "1", "yes", "y"}:
        return 1

    if normalized in {"false", "0", "no", "n"}:
        return 0

    return None


def load_mapping(mapping_path: str | Path) -> Dict[str, str]:
    """
    Load XML field mappings from a YAML configuration file.

    Args:
        mapping_path: Path to the YAML mapping file.

    Returns:
        Dictionary mapping structured field names to XML paths.
    """

    with open(mapping_path, "r", encoding="utf-8") as file:
        mapping = yaml.safe_load(file)

    return mapping["fields"]


def parse_xml_file(
    xml_path: str | Path,
    mapping: Dict[str, str],
) -> Dict[str, Any]:
    """
    Parse one XML healthcare message into a structured record.

    The function extracts XML values using configurable mappings
    and applies basic datatype normalization.

    Args:
        xml_path: Path to the XML input file.
        mapping: Dictionary mapping output fields to XML paths.

    Returns:
        Structured perinatal record dictionary.
    """

    root = ET.parse(xml_path).getroot()

    record: Dict[str, Any] = {
        field: _text(root, xpath)
        for field, xpath in mapping.items()
    }

    # Normalize numeric healthcare fields.
    for field in [
        "gestational_age_weeks",
        "gravida",
        "parity",
        "birth_weight_grams",
        "apgar_5min",
    ]:
        record[field] = _to_int(record.get(field))

    # Convert boolean-like NICU values into integer flags.
    record["admission_nicu"] = _to_bool_int(
        record.get("admission_nicu"),
    )

    record["file_name"] = Path(xml_path).name

    return record