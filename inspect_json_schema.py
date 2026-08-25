from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


MAX_DEPTH = 12
DEFAULT_SAMPLE_SIZE = 1000


def get_structure(
    value: Any,
    depth: int = 0,
) -> Any:
    """
    Convert actual JSON data into a structural schema.

    Values are replaced by their Python/JSON types.
    Lists additionally show the structure of their first item.
    """

    if depth >= MAX_DEPTH:
        return "..."

    if isinstance(value, dict):
        return {
            key: get_structure(
                val,
                depth + 1,
            )
            for key, val in value.items()
        }

    if isinstance(value, list):
        if not value:
            return {
                "type": "list",
                "items": None,
            }

        return {
            "type": "list",
            "items": get_structure(
                value[0],
                depth + 1,
            ),
        }

    if value is None:
        return "null"

    if isinstance(value, bool):
        return "bool"

    if isinstance(value, int):
        return "int"

    if isinstance(value, float):
        return "float"

    if isinstance(value, str):
        return "str"

    return type(value).__name__


def get_summary(
    value: Any,
    depth: int = 0,
) -> Any:
    """
    Similar to get_structure(), but also reports
    list lengths. Useful for understanding benchmark data.
    """

    if depth >= MAX_DEPTH:
        return "..."

    if isinstance(value, dict):
        return {
            key: get_summary(
                val,
                depth + 1,
            )
            for key, val in value.items()
        }

    if isinstance(value, list):
        if not value:
            return {
                "type": "list",
                "length": 0,
                "items": None,
            }

        return {
            "type": "list",
            "length": len(value),
            "items": get_summary(
                value[0],
                depth + 1,
            ),
        }

    if value is None:
        return "null"

    if isinstance(value, bool):
        return "bool"

    if isinstance(value, int):
        return "int"

    if isinstance(value, float):
        return "float"

    if isinstance(value, str):
        return "str"

    return type(value).__name__


def load_records(
    path: Path,
    limit: int,
) -> list[Any]:

    records: list[Any] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        # -------------------------------------------------
        # JSONL
        # -------------------------------------------------

        if path.suffix.lower() in {
            ".jsonl",
            ".ndjson",
        }:

            for line_number, line in enumerate(file, 1):

                if len(records) >= limit:
                    break

                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(
                        json.loads(line)
                    )

                except json.JSONDecodeError as exc:
                    print(
                        f"[WARNING] Invalid JSON at "
                        f"line {line_number}: {exc}",
                        file=sys.stderr,
                    )

        # -------------------------------------------------
        # JSON
        # -------------------------------------------------

        else:

            data = json.load(file)

            # A JSON file may contain either:
            #
            #   { ... }
            #
            # or:
            #
            #   [ {...}, {...} ]

            if isinstance(data, list):
                records.extend(
                    data[:limit]
                )

            else:
                records.append(data)

    return records


def make_schema_key(
    record: Any,
) -> str:

    structure = get_structure(record)

    return json.dumps(
        structure,
        ensure_ascii=False,
        sort_keys=True,
    )


def print_schema(
    schema: Any,
    count: int,
) -> None:

    print()
    print("=" * 80)
    print(
        f"SCHEMA | {count} record(s)"
    )
    print("=" * 80)

    print(
        json.dumps(
            schema,
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:

    if len(sys.argv) < 2:

        print(
            "Usage:\n"
            "  python inspect_json_schema.py <file> [sample_size]\n\n"
            "Examples:\n"
            '  python inspect_json_schema.py "data.jsonl"\n'
            '  python inspect_json_schema.py "data.jsonl" 1000\n'
            '  python inspect_json_schema.py "data.json"',
        )

        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.exists():

        print(
            f"[ERROR] File not found: {path}"
        )

        sys.exit(1)

    try:
        limit = (
            int(sys.argv[2])
            if len(sys.argv) >= 3
            else DEFAULT_SAMPLE_SIZE
        )

    except ValueError:

        print(
            "[ERROR] sample_size must be an integer."
        )

        sys.exit(1)

    if limit <= 0:

        print(
            "[ERROR] sample_size must be > 0."
        )

        sys.exit(1)

    print()
    print("=" * 80)
    print("JSON / JSONL STRUCTURE INSPECTOR")
    print("=" * 80)
    print(f"File         : {path}")
    print(f"Sample size  : {limit}")
    print()

    records = load_records(
        path,
        limit,
    )

    if not records:

        print(
            "[ERROR] No valid JSON records found."
        )

        sys.exit(1)

    print(
        f"Records read : {len(records)}"
    )

    # -----------------------------------------------------
    # Detect different schemas
    # -----------------------------------------------------

    schema_counter: Counter[str] = Counter()

    schema_objects: dict[str, Any] = {}

    for record in records:

        key = make_schema_key(record)

        schema_counter[key] += 1

        if key not in schema_objects:

            schema_objects[key] = get_structure(
                record
            )

    # -----------------------------------------------------
    # Print schemas
    # -----------------------------------------------------

    print()
    print(
        f"Different schemas found: "
        f"{len(schema_counter)}"
    )

    for index, (key, count) in enumerate(
        schema_counter.most_common(),
        start=1,
    ):

        schema = schema_objects[key]

        print()
        print(
            "#" * 80
        )
        print(
            f"SCHEMA {index}"
        )
        print(
            f"Records using schema: {count}"
        )
        print(
            "#" * 80
        )

        print(
            json.dumps(
                schema,
                ensure_ascii=False,
                indent=2,
            )
        )

    # -----------------------------------------------------
    # Print first-record summary
    # -----------------------------------------------------

    print()
    print("=" * 80)
    print("FIRST RECORD SUMMARY")
    print("=" * 80)

    print(
        json.dumps(
            get_summary(records[0]),
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print("=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()