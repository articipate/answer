"""Response validation and parsing."""

import json
import re
from typing import Any, Dict, List, Tuple

try:
    from json_repair import repair_json
    HAS_JSON_REPAIR = True
except Exception:
    HAS_JSON_REPAIR = False


class ResponseValidator:
    @staticmethod
    def extract_json(text: str) -> str:
        """Extract JSON from response text."""
        # Try to find JSON code block
        code_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if code_block:
            return code_block.group(1).strip()
        
        # Try to find JSON object/array
        # Look for {"rows": ...}
        rows_match = re.search(r'\{[\s\S]*"rows"[\s\S]*\}', text)
        if rows_match:
            return rows_match.group(0)
        
        # Look for array
        array_match = re.search(r'\[[\s\S]*\]', text)
        if array_match:
            return array_match.group(0)
        
        return text.strip()
    
    @staticmethod
    def parse_response(text: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Parse AI response to extract rows."""
        if not text:
            return [], "Empty response"
        
        json_str = ResponseValidator.extract_json(text)
        
        # Try direct parse
        try:
            data = json.loads(json_str)
            return ResponseValidator._extract_rows(data)
        except json.JSONDecodeError:
            pass
        
        # Try json repair
        if HAS_JSON_REPAIR:
            try:
                repaired = repair_json(json_str)
                data = json.loads(repaired)
                return ResponseValidator._extract_rows(data)
            except Exception:
                pass
        
        return [], f"Failed to parse response as JSON"
    
    @staticmethod
    def _extract_rows(data: Any) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        if isinstance(data, dict):
            if "rows" in data and isinstance(data["rows"], list):
                rows = [r for r in data["rows"] if isinstance(r, dict)]
                return rows, None
            # Single row object
            return [data], None
        elif isinstance(data, list):
            rows = [r for r in data if isinstance(r, dict)]
            return rows, None
        return [], "Invalid data structure"
    
    @staticmethod
    def clean_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize a row."""
        cleaned = {}
        for k, v in row.items():
            # Skip internal keys
            if k.startswith("_internal"):
                continue
            cleaned[k] = v
        return cleaned
