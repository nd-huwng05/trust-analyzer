from transformers import AutoTokenizer, pipeline, Qwen2_5_VLForConditionalGeneration, AutoProcessor, \
    AutoModelForCausalLM
import torch
from app.utils.logger import get_logger

device = "cuda" if torch.cuda.is_available() else "cpu"
llm_model_name = "app/pkg/Qwen2.5-1.5B-Instruct"
get_logger().info("Loading LLM model...")
qwen_tokenizer = AutoTokenizer.from_pretrained(llm_model_name, local_files_only=True)
qwen_processor = AutoProcessor.from_pretrained(llm_model_name, local_files_only=True)
qwen_model = AutoModelForCausalLM.from_pretrained(llm_model_name, device_map="auto", local_files_only=True)
get_logger().info("LLM model loaded.")