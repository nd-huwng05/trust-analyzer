import asyncio
from typing import List, Optional
from PIL import Image
import torch

from app.pkg.init import qwen_processor,qwen_model


def generate_sync(prompt_description):
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt_description}
    ]

    text_input = qwen_processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(qwen_model.device)

    output = qwen_model.generate(text_input, max_new_tokens=512)
    return qwen_processor.decode(output[0], skip_special_tokens=True)


async def generate(prompt: str, image_paths: Optional[List[str]] = None, max_new_tokens: int = 256) -> str:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, generate_sync, prompt, image_paths, max_new_tokens)
    return result