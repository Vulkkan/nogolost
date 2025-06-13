import requests
import json
from dotenv import load_dotenv
import os


load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_TOKEN = os.getenv('OPENROUTER_API_KEY')
MODEL =  os.getenv('MODEL')


HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_TOKEN}",
    "Content-Type": "application/json"
}


def chunkData(file) -> list:
    with open(file, encoding="utf-8") as f:
        text = f.read()

    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    max_chunk_chars = 3000  # ~750 tokens
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk_chars:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def extract_answer(generated_text):
    if "Answer:" in generated_text:
        return generated_text.split("Answer:")[-1].strip()
    return generated_text.strip()


def query_openrouter(prompt, context, model=MODEL):
    full_prompt = f"""You are an AI assistant that answers user questions strictly using the provided context. 

    Context:
    {context}

    User Question: {prompt}
    Answer:"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an AI assistant that answers questions using only the provided context."},
            {"role": "user", "content": full_prompt},
            {"role": "user", "content": f"User Question: {prompt}\nAnswer:"}
        ],
        "temperature": 0.3,
        "max_tokens": 512 
    }

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}", 0.0

    result = response.json()
    try:
        content = result['choices'][0]['message']['content']
        return extract_answer(content), 1.0
    except Exception as e:
        return f"Parsing Error: {str(e)}", 0.0


def reply(prompt, context_parts):
    # String Matching or Fuzzy Matching Instead of Raw Keyword Count
    top_k = 3  # bring this back up a little

    # First try to match route-related queries exactly
    exact_matches = [part for part in context_parts if prompt.lower() in part.lower()]

    if exact_matches:
        top_chunks = exact_matches[:top_k]
    else:
        prompt_keywords = prompt.lower().split()
        scored_chunks = []
        for part in context_parts:
            overlap = sum(1 for word in prompt_keywords if word in part.lower())
            scored_chunks.append((overlap, part))

        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        top_chunks = [part for _, part in scored_chunks[:top_k]]

    answers = []
    for part in top_chunks:
        answer, confidence = query_openrouter(prompt, part)
        answers.append((answer, confidence))

    best_answer = max(answers, key=lambda x: x[1])[0]
    return best_answer


# def reply(prompt, context_parts):
#     answers_dict = {}
#     for i, part in enumerate(context_parts):
#         answer, confidence = query_openrouter(prompt, part)
#         answers_dict[f"Chunk {i+1}"] = {answer: confidence}
#     best_answer = max(answers_dict.values(), key=lambda x: list(x.values())[0])
#     best_text = list(best_answer.keys())[0]
#     return best_text

