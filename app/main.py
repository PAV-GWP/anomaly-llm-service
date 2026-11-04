from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.schemas import MetricsRequest, AnalysisResponse
from app.detector import analyze_time_series
from app.database import init_db, save_log, get_recent_logs
from app.llm_service import generate_recommendation

# 1. Функция жизненного цикла (Lifespan): запускается один раз при старте сервера
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Автоматически создаём таблицу в базе данных при запуске
    yield

# 2. Создаём приложение с красивым заголовком для документации Swagger
app = FastAPI(
    title="AnomalyLLM Service",
    description="Микросервис детекции аномалий во временных рядах и генерации отчетов через LLM",
    version="1.0.0",
    lifespan=lifespan
)

# 3. Базовый роут проверки жизнеспособности (Healthcheck)
@app.get("/")
def health_check():
    return {"status": "ok", "service": "AnomalyLLM"}

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_metrics(payload: MetricsRequest):
    # Шаг 1: Математический анализ временного ряда через Pandas
    metrics = analyze_time_series(payload.temperatures)
    
    # Шаг 2: Генерация понятной рекомендации (через LLM или fallback)
    rec_text = generate_recommendation(payload.server_id, metrics)
    
    # Шаг 3: Сохранение результатов в историю SQLite
    save_log(
        server_id=payload.server_id,
        max_temp=metrics["max_temp"],
        status=metrics["status"],
        trend=metrics["trend"]
    )
    
    # Шаг 4: Формирование ответа по схеме AnalysisResponse
    return AnalysisResponse(
        server_id=payload.server_id,
        status=metrics["status"],
        anomalies_found=metrics["anomalies"],
        max_temp=metrics["max_temp"],
        recommendation=rec_text
    )

@app.get("/api/v1/history")
def get_history(limit: int = 5):
    return get_recent_logs(limit=limit)