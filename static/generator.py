import ollama
import json
import re
import random

def generate_questions_via_ollama(n=10, topic="разное"):
    prompt = (
        f"Сгенерируй {n} разных коротких вопросов на русском на тему '{topic}' "
        f"с ответами Правда или Ложь. Формат строго JSON: "
        f"[{{\"text\": \"вопрос\", \"answer\": true}}, ...]"
    )

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.get("message", {}).get("content", "").strip()
    match = re.search(r"\[.*\]", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception as e:
            print("❌ Ошибка парсинга JSON:", e)

    return []
