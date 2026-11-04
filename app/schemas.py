from pydantic import BaseModel, Field

class MetricsRequest(BaseModel): #что присылает клиент
    server_id: str = Field(..., description="ID Сервера")
    temperatures: list[float]= Field(..., min_length=1, description="Список температур")

class AnalysisResponse(BaseModel): # что возвращает наш сервис
    server_id: str
    status: str
    anomalies_found: list[float]
    max_temp: float
    recommendation: str