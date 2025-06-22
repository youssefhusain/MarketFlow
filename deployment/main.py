from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from models import prophet_forecast, ann_forecast

app = FastAPI()

class TimeSeriesEntry(BaseModel):
    date: str
    Adj_Close: float

class ForecastRequest(BaseModel):
    data: List[TimeSeriesEntry]
    periods: int = 60

@app.post("/forecast/prophet")
def forecast_with_prophet(request: ForecastRequest):
    try:
        df = pd.DataFrame([{"date": entry.date, "Adj Close": entry.Adj_Close} for entry in request.data])
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        result, metrics = prophet_forecast(df, request.periods)
        return {"forecast": result, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/forecast/ann")
def forecast_with_ann(request: ForecastRequest):
    try:
        df = pd.DataFrame([{"date": entry.date, "Adj Close": entry.Adj_Close} for entry in request.data])
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        result, metrics = ann_forecast(df)
        return {"forecast": result, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
