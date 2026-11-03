"""Verify contract syntax and check synthetic input/output vectors against the schemas."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = json.loads((ROOT / "conformance/cases.json").read_text(encoding="utf-8"))
    sunat = json.loads((ROOT / "contracts/sunat/validity.schema.json").read_text())
    reniec = json.loads((ROOT / "contracts/reniec/identity.prototype.schema.json").read_text())
    for schema in (sunat, reniec):
        Draft202012Validator.check_schema(schema)

    def validator(schema, name):
        return Draft202012Validator(schema["$defs"][name], format_checker=FormatChecker())

    query = validator(sunat, "ValidityQuery")
    result = validator(sunat, "ValidityResult")
    for case in cases["query_cases"]:
        value = {**cases["query"], **case["patch"]}
        assert query.is_valid(value) == case["valid"], case["id"]
    for case in cases["response_cases"]:
        if "expected" in case:
            result.validate(case["expected"])
    identity = validator(reniec, "Identity")
    for record in cases["identity_records"]:
        identity.validate(record)
    query = validator(reniec, "IdentityQuery")
    for case in cases["identity_cases"]:
        assert query.is_valid({"dni": case["dni"]}) != case.get("invalid", False), case["id"]
    print("Contracts and shared vectors are valid.")


if __name__ == "__main__":
    main()
