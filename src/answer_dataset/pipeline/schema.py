"""Schema validation and inference."""

import json
from typing import Any, Dict, Optional
from jsonschema import validate, ValidationError


class SchemaHandler:
    @staticmethod
    def infer_schema(example: Dict[str, Any]) -> Dict[str, Any]:
        """Infer JSON schema from example row."""
        def infer_type(value):
            if isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, list):
                if value:
                    return {"type": "array", "items": infer_type(value[0])}
                return {"type": "array"}
            elif isinstance(value, dict):
                props = {}
                for k, v in value.items():
                    props[k] = infer_type(v)
                return {"type": "object", "properties": props}
            elif value is None:
                return {"type": "null"}
            return {"type": "string"}
        
        properties = {}
        required = []
        for key, value in example.items():
            properties[key] = infer_type(value)
            if value is not None:
                required.append(key)
        
        schema = {
            "type": "object",
            "properties": properties,
        }
        if required:
            schema["required"] = required
        return schema
    
    @staticmethod
    def validate_row(row: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        if not schema:
            return True, None
        try:
            validate(instance=row, schema=schema)
            return True, None
        except ValidationError as e:
            return False, e.message
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_format(example: str) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Validate example JSON format."""
        try:
            data = json.loads(example)
            if isinstance(data, dict):
                return True, None, data
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return True, None, data[0]
            else:
                return False, "Example must be a JSON object or array of objects", None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}", None
        except Exception as e:
            return False, str(e), None
