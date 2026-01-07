import torch
from vllm import LLM, SamplingParams
from utils.prompts import build_messages_vllm, strip_reasoning

def run(model: str, rows: list, max_tokens: int, temperature: float, top_p: float):
    if 'mistral' in model:
        llm = LLM(model=model, tensor_parallel_size=max(1, torch.cuda.device_count()), trust_remote_code=True, tokenizer_mode="mistral")#, 
    else:
        llm = LLM(model=model, tensor_parallel_size=max(1, torch.cuda.device_count()), trust_remote_code=True)#, max_model_len=8192*4)
    tok = llm.get_tokenizer()
    sampling = SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens)
    outs = llm.chat(rows, sampling)
    texts = [o.outputs[0].text for o in outs]
    return texts
