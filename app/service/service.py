from platform import processor

from app.models.models import InfoProduct
from app.pkg import init
from app.pkg.ai import generate_sync
from app.utils.json import extract_json
from app.utils.prompt import Prompt


async def description_analyze(info : InfoProduct):
    prompt = Prompt(info)
    prompt_description = prompt.generate_description_prompt()
    result = generate_sync(prompt_description)
    result = extract_json(result)
    return result

async def comment_analyze(info : InfoProduct):
    prompt = Prompt(info)
    prompt_comment = prompt.generate_comment_prompt()
    result = generate_sync(prompt_comment)
    result = extract_json(result)
    return result

def full_analyze(text, image, comment):
    prompt_full = Prompt.generate_full_prompt(image, comment, text)
    result = generate_sync(prompt_full)
    result = extract_json(result)
    return result