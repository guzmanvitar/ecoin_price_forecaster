"""
API for serving of the forecasting models.
"""

import datetime
import pickle
from enum import auto

from fastapi import FastAPI
from fastapi_utils.enums import StrEnum

from src.constants import ARIMA_DEAFULT_ORDER, MODELS_FORECASTING
from src.models.forecasters import ARIMAModel  # noqa

ethereum_model_name = (
    f"ethereum_ARIMA_{'.'.join(list([str(o) for o in ARIMA_DEAFULT_ORDER]))}_0.0.0.0"
)
ethereum_model_path = MODELS_FORECASTING / f"{ethereum_model_name}_latest.pickle"
with open(ethereum_model_path, "rb") as file:
    ethereum_model = pickle.load(file)

bitcoin_model_name = f"bitcoin_ARIMA_{'.'.join(list([str(o) for o in ARIMA_DEAFULT_ORDER]))}"
bitcoin_model_path = MODELS_FORECASTING / f"{bitcoin_model_name}_0.0.0.0_latest.pickle"
with open(bitcoin_model_path, "rb") as file:
    bitcoin_model = pickle.load(file)

app = FastAPI(
    title="Ecoin Forecast API",
    description="Forecasting API for the fullstack ML challenge",
    contact={"Dev name": "Guzman Vitar", "email": "guzmanvitar@gmail.com"},
)


class AvailableCoins(StrEnum):
    bitcoin = auto()
    ethereum = auto()


@app.get("/")
def index():
    return "Welcome to the forecasting API for the fullstack ML challenge"


@app.get("/")
def root():
    return


@app.get("/predictions/{coin_id}/{target_date}")
def get_predictions(coin_id: AvailableCoins, target_date: datetime.date):
    # Predict according to passed coin
    if coin_id == "ethereum":
        predictions = ethereum_model.forecast(target_date=target_date)
    elif coin_id == "bitcoin":
        predictions = bitcoin_model.forecast(target_date=target_date)
    else:
        raise ValueError(
            "No model trained for required coin. Coin must be one of"
            f" {' '.join([coin for coin in AvailableCoins])}"
        )

    return predictions


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
