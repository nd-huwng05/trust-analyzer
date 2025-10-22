import json
import re

def extract_json(text: str):
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not matches:
        matches = re.findall(r"(\{[\s\S]*?\})", text)

    if not matches:
        return {"score": 0, "comment": "Không tìm thấy JSON hợp lệ."}

    json_str = matches[-1].strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        json_str_escaped = re.sub(r'(?<!\\)"', r'\"', json_str)
        json_str_escaped = re.sub(r'\n', ' ', json_str_escaped)
        try:
            return json.loads(json_str_escaped)
        except Exception:
            safe_comment = json_str_escaped[:1000]  # giới hạn dài comment
            return {"score": 0, "comment": safe_comment}
