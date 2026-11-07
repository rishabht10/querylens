import re
DATE_RE = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?$")

def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

def recommend_chart(cols, rows):
    if len(rows) < 2 or len(cols) < 2:
        return None
    numeric = [i for i in range(len(cols))
               if all(_num(r[i]) for r in rows if r[i] is not None)]
    label = next((i for i in range(len(cols)) if i not in numeric), None)
    if label is None:
        return ({"type": "scatter", "label_index": None, "value_indices": numeric[:2]}
                if len(numeric) == 2 else None)
    values = [i for i in numeric if i != label][:3]
    if not values:
        return None
    is_date = all(DATE_RE.match(str(r[label])) for r in rows)
    return {"type": "line" if is_date else "bar",
            "label_index": label, "value_indices": values}