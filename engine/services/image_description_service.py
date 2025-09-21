# services/image_processing.py
from __future__ import annotations
import bentoml
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import cv2
from pathlib import Path
from typing import List, Dict, Any

# NO MORE bentoml.io imports!

SHARED_DATA_PATH = Path(__file__).parent.parent.parent / "shared_data"

@bentoml.service(resources={"cpu": "2", "memory": "4Gi"})
class PreprocessingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = "HuggingFaceTB/SmolVLM2-256M-Video-Instruct"
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.processor.image_processor.size = {"longest_edge": 600}

    def _load_image(self, path: str) -> Image.Image:
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img)

    # THE FIX: The return type hint is Dict[str, torch.Tensor].
    # BentoML's internal client sees this and knows to use a high-performance
    # binary protocol instead of JSON.
    @bentoml.api
    def preprocess(self, filenames: List[str]) -> Dict[str, torch.Tensor]:
        batch_messages = []
        for name in filenames:
            file_path = SHARED_DATA_PATH / name
            image = self._load_image(str(file_path))
            messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": "Describe this image in detail."}]}]
            batch_messages.append(messages)
        
        inputs = self.processor.apply_chat_template(
            batch_messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt", padding=True,
        )
        # The tensors are returned directly. No .tolist() conversion.
        return {k: v for k, v in inputs.items()}

@bentoml.service(resources={"gpu": 1, "memory": "4Gi"})
class InferenceService:
    preprocessor = bentoml.depends(PreprocessingService)
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = "HuggingFaceTB/SmolVLM2-256M-Video-Instruct"
        
        model_dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_name,
            attn_implementation="flash_attention_2" if self.device == "cuda" else None,
            dtype=model_dtype
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(model_name)

    @bentoml.api
    async def predict(self, filenames: List[str]) -> List[str]:
        # This call now receives a dictionary of native torch.Tensor objects.
        batch_inputs = await self.preprocessor.to_async.preprocess(filenames)
        
        # We only need to ensure the tensors are on the correct device.
        # The dtypes are preserved during the binary transfer.
        batch_inputs = {k: v.to(self.device) for k, v in batch_inputs.items()}

        with torch.inference_mode():
            outputs = self.model.generate(**batch_inputs, max_new_tokens=256)
            
        decoded_texts = self.processor.batch_decode(outputs, skip_special_tokens=True)
        return [text.split("Assistant: ")[-1].strip() for text in decoded_texts]