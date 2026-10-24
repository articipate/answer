"""CSV exporter."""

import csv
import json
from typing import List, Dict, Any


class CSVExporter:
    @staticmethod
    def export(rows: List[Dict[str, Any]], path: str):
        if not rows:
            return
        
        # Get all keys
        all_keys = set()
        for row in rows:
            all_keys.update(row.keys())
        fieldnames = sorted(list(all_keys))
        
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                # Convert complex types to JSON strings
                out_row = {}
                for k in fieldnames:
                    v = row.get(k)
                    if isinstance(v, (dict, list)):
                        out_row[k] = json.dumps(v, ensure_ascii=False)
                    elif v is None:
                        out_row[k] = ""
                    else:
                        out_row[k] = v
                writer.writerow(out_row)
    
    @staticmethod
    def export_from_dataset_rows(dataset_rows, path: str):
        rows = [r.data for r in dataset_rows]
        CSVExporter.export(rows, path)
