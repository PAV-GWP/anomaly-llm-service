import os
import httpx
from dotenv import load_dotenv

# Читаем переменные из файла .env при загрузке модуля
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


def create_analysis_prompt(server_id: str, metrics: dict) -> str:
    return f"""Ты ведущий системный инженер инфраструктуры.
Проанализируй замеры сервера '{server_id}':
- Максимальная зафиксированная температура: {metrics.get('max_temp')}°C
- Медианная температура: {metrics.get('median_temp')}°C
- Выявленные аномалии: {metrics.get('anomalies')}
- Направление тренда: {metrics.get('trend')}

Сформулируй краткую инженерную рекомендацию (1-2 четких предложения): 
что происходит с сервером и какое действие нужно предпринять дежурной смене. 
Отвечай строго на русском языке, без приветствий и лишних вступлений."""


def generate_recommendation(server_id: str, metrics: dict) -> str:
    # Отладка: проверяем, видит ли Python ключ из .env
    print(f"\n[DEBUG] Текущий ключ: '{GROQ_API_KEY[:8]}...' | Модель: '{LLM_MODEL}'")

    if not GROQ_API_KEY or GROQ_API_KEY == "your_key_here":
        print("[DEBUG] Сработал Fallback: ключ пустой или равен 'your_key_here'")
        return _fallback_recommendation(server_id, metrics)

    prompt = create_analysis_prompt(server_id, metrics)
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Ты эксперт по мониторингу серверов. Отвечай кратко, профессионально и по делу."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1000
        
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(GROQ_ENDPOINT, json=payload, headers=headers)
            print(f"[DEBUG] Код ответа Groq: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                print(f"[DEBUG] Ошибка от сервера Groq: {response.text}")
                return _fallback_recommendation(server_id, metrics)
                
    except Exception as e:
        print(f"[DEBUG] Ошибка соединения/сети: {e}")
        return _fallback_recommendation(server_id, metrics)

def _fallback_recommendation(server_id: str, metrics: dict) -> str:
    """Резервный локальный генератор (работает без интернета и ключей)."""
    if metrics.get("status") == "anomaly":
        return (
            f"[Правило] На сервере {server_id} зафиксирован перегрев (макс: {metrics.get('max_temp')}°C, "
            f"тренд: {metrics.get('trend')}). Проверьте систему охлаждения и завершите пиковые процессы."
        )
    return f"[Правило] Показатели сервера {server_id} находятся в пределах нормы. Дополнительных мер не требуется."