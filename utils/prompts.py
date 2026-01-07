def build_messages_vllm(question: str, data_url: list, system: str):
    user_content = [
         {"type": "text","text": question},
    ]
    for img in data_url:
        user_content.append({ "type": "image_pil","image_pil": img})
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content}
    ]

def build_messages_litellm(question: str, data_url: list, system: str):
    user_content = [
         {"type": "text", "text": question.strip()}
    ]
    for img in data_url:
        user_content.append(
            {"type": "image_url", "image_url": {"url": img}}
        )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content}
    ]

def strip_reasoning(text: str) -> str:
    if not isinstance(text, str):
        return ""
    for tag in ["</think>", "</thinking>", "<think>", "<thinking>"]:
        if tag in text:
            text = text.split(tag)[-1].strip()
    return text.strip()
