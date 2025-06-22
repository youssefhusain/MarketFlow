# models.py

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

# --- Prophet Forecasting ---
def prophet_forecast(df: pd.DataFrame, periods: int = 60):
    df_reset = df.reset_index()
    df_prophet = df_reset[["date", "Adj Close"]].rename(columns={"date": "ds", "Adj Close": "y"})

    model = Prophet()
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    forecast_actual = forecast[forecast['ds'] <= df_prophet['ds'].max()]
    y_true = df_prophet['y'].values
    y_pred = forecast_actual['yhat'].values

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    metrics = {"mae": mae, "rmse": rmse, "mape": mape}
    forecast_result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)
    return forecast_result.to_dict(orient="records"), metrics


# --- ANN Forecasting ---
def ann_forecast(df: pd.DataFrame, lag: int = 10, test_size: int = 120):
    np_data = df["Adj Close"].dropna().values

    X, Y = [], []
    for i in range(0, len(np_data) - lag):
        x = np_data[i : i + lag]
        y = np_data[i + lag]
        X.append(x)
        Y.append(y)

    X = np.array(X)
    Y = np.array(Y)

    X_train, X_test = X[:-test_size], X[-test_size:]
    y_train, y_test = Y[:-test_size], Y[-test_size:]

    input_layer = Input(shape=(X_train.shape[1],))
    h1 = Dense(32, activation="relu")(input_layer)
    h2 = Dense(16, activation="relu")(h1)
    output_layer = Dense(1)(h2)

    model = Model(inputs=input_layer, outputs=output_layer)
    model.compile(optimizer="adam", loss="mse", metrics=["mse", "mape"])
    model.fit(X_train, y_train, epochs=100, validation_data=(X_test, y_test), verbose=0)

    pred_te = model.predict(X_test).flatten()

    mae = mean_absolute_error(y_test, pred_te)
    rmse = mean_squared_error(y_test, pred_te, squared=False)
    mape = mean_absolute_percentage_error(y_test, pred_te) * 100

    test_idx = df.index[-len(y_test):]
    prediction = pd.DataFrame({"date": test_idx, "prediction": pred_te})
    forecast_result = prediction.tail(test_size)

    metrics = {"mae": mae, "rmse": rmse, "mape": mape}
    return forecast_result.to_dict(orient="records"), metrics
