"""
Main module for ecoin price forecasting models training. Run

    python src/models/train_forecasters.py --help

for usage help.
"""

import argparse

from src.constants import ARIMA_DEAFULT_ORDER
from src.models.forecasters import ARIMAModel

if __name__ == "__main__":
    parser = argparse.ArgumentParser("train_forecasters")

    parser.add_argument(
        "-c",
        "--coin",
        help="Coin to train forecaster for",
    )

    parser.add_argument(
        "-m",
        "--model",
        default="ARIMA",
        help="Model to train",
    )

    args = parser.parse_args()

    if args.model == "ARIMA":
        model = ARIMAModel(coin_id=args.coin)

        # Load data
        model.load_train_data()

        # Train model with best identified params
        model.fit(order=(ARIMA_DEAFULT_ORDER))
    else:
        # For now only ARIMA
        raise ValueError("Model not implemented")
