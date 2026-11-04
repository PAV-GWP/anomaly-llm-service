import pandas as pd

def analyze_time_series(temperatures: list[float]) -> dict:
    s = pd.Series(temperatures)
    clean_s= s[s>0]

    if clean_s.empty:
        return {
            "status": "error",
            "anomalies": [],
            "max_temp": 0.0,
            "median_temp": 0.0,
            "trend": "нет данных"
        }
    mean_val = float(clean_s.mean()) # среднее арифм - .mean
    std_val = float(clean_s.std()) if len(clean_s) > 1 else 0.0 # .std - стандарт отклонение
    max_val = float(clean_s.max())
    median_val= float(clean_s.median())

    dynamic_threshold = mean_val + (2 * std_val) if std_val > 0 else 80.0
    anomalies=  clean_s[(clean_s>80.0) | (clean_s > dynamic_threshold)].tolist()

    #Выделение тренда
    if len(clean_s)>= 3:
        rolling_series = clean_s.rolling(window = 2).mean().dropna()
        trend = "растущий" if rolling_series.iloc[-1] > rolling_series.iloc[0] else "стабильный/падающий"
    else:
        trend = "недостаточно точек для тренда"
    return {
        "status": "anomaly" if anomalies else "normal",
        "anomalies": [round(x,2) for x in anomalies],
        "max_temp": round(max_val, 2),
        "median_temp": round(median_val, 2),
        "trend": trend
    }