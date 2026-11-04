import pytest
from app.detector import analyze_time_series


def test_normal_temperature_series():
    """Проверка нормального режима: отсутствие аномалий и корректный тренд."""
    data = [42.0, 43.0, 44.0, 45.0, 46.0]
    result = analyze_time_series(data)

    assert result["status"] == "normal"
    assert len(result["anomalies"]) == 0
    assert result["max_temp"] == 46.0
    assert result["median_temp"] == 44.0
    assert result["trend"] == "растущий"


def test_anomaly_detection_by_threshold():
    """Проверка фиксации критического перегрева выше 80°C."""
    data = [40.0, 42.0, 41.0, 95.0, 43.0]
    result = analyze_time_series(data)

    assert result["status"] == "anomaly"
    assert 95.0 in result["anomalies"]
    assert result["max_temp"] == 95.0


def test_empty_or_invalid_data():
    """Проверка защитной логики при пустых или отрицательных замерах."""
    data = [-10.0, 0.0]  # Фильтр s[s > 0] должен отсеять все точки
    result = analyze_time_series(data)

    assert result["status"] == "error"
    assert result["anomalies"] == []
    assert result["max_temp"] == 0.0
    assert result["trend"] == "нет данных"