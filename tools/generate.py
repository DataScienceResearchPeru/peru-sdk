"""Generate native models from the deliberately small contract subset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = (
    ("sunat", ROOT / "contracts/sunat/validity.schema.json"),
    ("reniec", ROOT / "contracts/reniec/identity.prototype.schema.json"),
)


def go_name(value: str) -> str:
    return "".join({"ruc": "RUC", "dni": "DNI"}.get(p, p.title()) for p in value.split("_"))


def check_shape(shape: dict) -> None:
    if set(shape) - {"type", "additionalProperties", "required", "properties"}:
        raise ValueError("unsupported object keyword")
    if shape["type"] != "object" or shape["additionalProperties"] is not False:
        raise ValueError("only closed objects are supported")
    if set(shape["required"]) != set(shape["properties"]):
        raise ValueError("this generator supports required fields only")
    for spec in shape["properties"].values():
        allowed = {"type", "description"}
        if spec["type"] == "string":
            allowed |= {"pattern", "format"}
            if "format" in spec and spec["format"] != "date":
                raise ValueError("unsupported format")
        elif spec["type"] == "integer":
            allowed |= {"minimum", "maximum"}
        elif spec["type"] == "array" and spec.get("items") == {"type": "string"}:
            allowed |= {"items"}
        else:
            raise ValueError("unsupported field type")
        if set(spec) - allowed:
            raise ValueError("unsupported field keyword")


def render_python(shapes: dict) -> str:
    has_dates = any(s.get("format") == "date" for shape in shapes.values() for s in shape["properties"].values())
    has_patterns = any("pattern" in s for shape in shapes.values() for s in shape["properties"].values())
    out = [
        '"""Contract models. Regenerate with python3 tools/generate.py."""',
        "from dataclasses import dataclass",
    ]
    if has_dates:
        out.append("from datetime import date")
    if has_patterns:
        out.append("import re")
    types = {"string": "str", "integer": "int", "array": "tuple[str, ...]"}
    for name, shape in shapes.items():
        out += ["", "@dataclass(frozen=True)", f"class {name}:"]
        for field, spec in shape["properties"].items():
            out.append(f"    {field}: {types[spec['type']]}")
        out += ["", "    def __post_init__(self) -> None:"]
        for field, spec in shape["properties"].items():
            attr = f"self.{field}"
            if spec["type"] == "array":
                test = f"type({attr}) is not tuple or any(type(v) is not str for v in {attr})"
            else:
                test = f"type({attr}) is not {types[spec['type']]}"
            out += [f"        if {test}:", f'            raise ValueError("{field}: invalid type")']
            if "pattern" in spec:
                out += [f"        if re.fullmatch({spec['pattern']!r}, {attr}, flags=re.ASCII) is None:",
                        f'            raise ValueError("{field}: invalid format")']
            for key, op in (("minimum", "<"), ("maximum", ">")):
                if key in spec:
                    out += [f"        if {attr} {op} {spec[key]}:", f'            raise ValueError("{field}: out of range")']
            if spec.get("format") == "date":
                out += ["        try:", f"            parsed = date.fromisoformat({attr})", "        except ValueError:",
                        f'            raise ValueError("{field}: invalid date") from None',
                        f"        if parsed.isoformat() != {attr}:", f'            raise ValueError("{field}: expected YYYY-MM-DD")']
    return "\n".join(out) + "\n"


def render_go(package: str, shapes: dict) -> str:
    out = ["// Contract models. Regenerate with python3 tools/generate.py.", f"package {package}",
           'import ("fmt"; "regexp"; "time")']
    # Imports are inferred, so new packages do not need dummy references.
    patterns = any("pattern" in s for shape in shapes.values() for s in shape["properties"].values())
    dates = any(s.get("format") == "date" for shape in shapes.values() for s in shape["properties"].values())
    imports = ['"fmt"'] + (['"regexp"'] if patterns else []) + (['"time"'] if dates else [])
    out[2] = "import (" + ";".join(imports) + ")"
    types = {"string": "string", "integer": "int64", "array": "[]string"}
    for name, shape in shapes.items():
        out.append(f"type {name} struct {{")
        for field, spec in shape["properties"].items():
            out.append(f'{go_name(field)} {types[spec["type"]]} `json:"{field}"`')
        out += ["}", f"func (m {name}) Validate() error {{"]
        for field, spec in shape["properties"].items():
            attr = "m." + go_name(field)
            if spec["type"] == "array":
                out.append(f'if {attr} == nil {{ return fmt.Errorf("{field}: expected an array") }}')
            if "pattern" in spec:
                var = name[0].lower() + name[1:] + go_name(field) + "Pattern"
                out.append(f'if !{var}.MatchString({attr}) {{ return fmt.Errorf("{field}: invalid format") }}')
            for key, op in (("minimum", "<"), ("maximum", ">")):
                if key in spec:
                    out.append(f'if {attr} {op} {spec[key]} {{ return fmt.Errorf("{field}: out of range") }}')
            if spec.get("format") == "date":
                out.append(f'if t, err := time.Parse("2006-01-02", {attr}); err != nil || t.Format("2006-01-02") != {attr} {{ return fmt.Errorf("{field}: expected YYYY-MM-DD") }}')
        out += ["return nil", "}"]
        for field, spec in shape["properties"].items():
            if "pattern" in spec:
                var = name[0].lower() + name[1:] + go_name(field) + "Pattern"
                out.append(f"var {var} = regexp.MustCompile({json.dumps(spec['pattern'])})")
    return subprocess.run(["gofmt"], input="\n".join(out), text=True, capture_output=True, check=True).stdout


def outputs() -> dict[Path, str]:
    result = {}
    for package, path in CONTRACTS:
        schema = json.loads(path.read_text())
        if set(schema) - {"$schema", "$id", "description", "$defs"}:
            raise ValueError("unsupported root keyword")
        shapes = schema["$defs"]
        for shape in shapes.values():
            check_shape(shape)
        result[ROOT / f"sdk-go/{package}/models.gen.go"] = render_go(package, shapes)
        result[ROOT / f"sdk-python/src/peru_sdk/{package}/models.py"] = render_python(shapes)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dirty = []
    for path, content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                dirty.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if dirty:
        print("Models need regeneration: " + ", ".join(dirty), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
