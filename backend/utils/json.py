import json
import re

def extract_json(text: str):
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not matches:
        matches = re.findall(r"(\{[\s\S]*?\})", text)

    if not matches:
        print("⚠️ Không tìm thấy JSON trong chuỗi.")
        return {}

    json_str = matches[-1].strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        json_str_fixed = json_str.replace("'", '"')
        try:
            return json.loads(json_str_fixed)
        except Exception as e:
            print(" Lỗi parse JSON:", e)
            print("Nội dung JSON:", json_str)
            return {}
