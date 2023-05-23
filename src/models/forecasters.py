"""
Defines classes for coin forecasting
"""

import datetime
import pickle
from collections.abc import Mapping
from enum import Enum
from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from numpy.typing import ArrayLike
from sklearn.metrics import mean_squared_error
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResultsWrapper
from statsmodels.tsa.stattools import adfuller

from src.constants import (
    ARIMA_DEAFULT_ORDER,
    COIN_ID,
    COIN_PRICE,
    DATE,
    MODELS_FORECASTING,
    MODELS_FORECASTING_HISTORY,
)
from src.db_scripts import db_connection, db_mappings
from src.logger_definition import get_logger

logger = get_logger(__file__)


class DataSources(str, Enum):
    FILE = "file"
    DATABASE = "database"


class ForecastingModel:
    def __init__(self, data=None):
        self.train_data = data

    def fit(self):
        """
        Fit the forecasting model to the training data.

        """
        raise NotImplementedError("Subclasses must implement fit() method.")

    def forecast(self, X: ArrayLike) -> ArrayLike:
        """
        Generate forecasts using the trained model.

        Parameters:
        X (array-like): The input features for forecasting.

        Returns:
        array-like: The forecasted values.
        """
        raise NotImplementedError("Subclasses must implement forecast() method.")

    def load_train_data(self, source: DataSources = DataSources.DATABASE, **kwargs):
        """
        Load historical data for the forecasting model.

        Parameters:
        source (str): The data source. Options: 'file', 'database'.
        **kwargs: Additional keyword arguments specific to the data source.

        Keyword Arguments:
        - For 'file' source:
            - file_path (pathlib.Path): The file path to the historical data file.
            - start_date (datetime.date | None, Optional): Starting date for the historic data.
                Defaults to None.
        - For 'database' source:
            - table (str): The name of the table in the PostgreSQL database.
            - start_date (datetime.date | None, Optional): Starting date for the historic data.
                Defaults to None.
        """
        sources = [source.value for source in DataSources]

        if source.value not in sources:
            raise ValueError(f"Invalid data source. Please specify {''.join(sources)}")

        else:
            if source == DataSources.FILE:
                data = self._load_from_file(**kwargs)
            elif source == DataSources.DATABASE:
                data = self._load_from_database(**kwargs)

            # Format data
            data[DATE] = pd.to_datetime(data[DATE])
            data = data.sort_values([COIN_ID, DATE])

            # Sanity checks
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

            for coin in data[COIN_ID].unique():
                coin_data = data[data[COIN_ID] == coin]
                coin_data["delta_days"] = coin_data[DATE].diff() / datetime.timedelta(days=1)
                if (missing_dates := coin_data["delta_days"].fillna(1.0) != 1.0).sum() > 0:
                    num_missing_dates = coin_data.loc[missing_dates, "delta_days"].sum()
                    logger.warning(f"{int(num_missing_dates)} data points missing for {coin}")
                if (latest_scrape_date := coin_data[DATE].max()) < yesterday:
                    logger.warning(
                        f"Scraping is outdated for {coin}, latest scraped date is"
                        f" {latest_scrape_date}"
                    )

            self.train_data = data

        return data

    def _load_from_file(self, file_path: Path, start_date: datetime.date | None = None):
        """
        Load historical data from a file.

        Parameters:
        file_path (Path): The file path to the historical data file.
        start_date (datetime.date | None, Optional): Starting date for the historic data.
            Defaults to None.
        """
        # Read data from CSV file
        data = pd.read_csv(file_path)
        data[DATE] = pd.to_datetime(data[DATE])

        if start_date:
            data = data[data[DATE] >= start_date]

        return data

    def _load_from_database(
        self,
        table: db_mappings.Base = db_mappings.CoingeckoScrapedData,
        start_date: datetime.date | None = None,
    ):
        """
        Load historical data from a database.

        Parameters:
        table (db_mappings.Base): Sqlalchemy declarative base.
        start_date (datetime.date | None, Optional): Starting date for the historic data.
            Defaults to None.
        """
        # Create a SQLAlchemy connection
        db = db_connection.PostgresDb()

        # Create a session
        with db.Session() as my_session:
            # Query the data from the specified table
            if start_date:
                date_col = getattr(table, DATE)

                data = my_session.query(table).filter(date_col > start_date).all()
            else:
                data = my_session.query(table).all()

            # Convert data to pandas DataFrame
            df = pd.DataFrame([row.__dict__ for row in data]).drop(columns=["_sa_instance_state"])

            # Close the session
            my_session.close()

        return df

    def plot_time_series(
        self,
        coin_ids: list[str] | None = None,
        coin_col: str = COIN_ID,
        date_col: str = DATE,
        price_col: str = COIN_PRICE,
    ):
        """
        Plots training data time series using the specified date and price columns.

        Args:
            coin_ids (list[str] | None, Optional): Name of the coins to plot. By default plots every
                coin available.
            coin_col (str, Optional): The name of the column representing the coin type.
            date_col (str, Optional): The name of the column representing the date.
            price_col (str, Optional): The name of the column representing the price.
        """
        # Use train data, if not defined yet load from db
        if self.train_data is None:
            self.load_train_data()

        data = self.train_data

        # Set the Seaborn style
        sns.set_theme(style="darkgrid")

        # Get coin types
        if coin_ids:
            coins = coin_ids
        else:
            coins = data[coin_col].unique()

        # Plot one line plot for every coin type
        _, ax = plt.subplots(figsize=(10, 6))

        for coin in coins:
            # Get data for the coin
            coin_data = data[data[COIN_ID] == coin]

            # Plot the time series
            sns.lineplot(data=coin_data, x=date_col, y=price_col, label=coin, ax=ax)

        # Format the plot
        ax.set_title("Coin Price Over Time")
        ax.set_xlabel(f"{' '.join(date_col.title().split('_'))}")
        ax.set_ylabel(f"{' '.join(price_col.title().split('_'))}")
        plt.xticks(rotation=45)

        # Show legend
        ax.legend()

        # Show the plot
        plt.show()

    def parallel_year_plot(self, coin_id: str, date_col: str = DATE, price_col: str = COIN_PRICE):
        """Plots coin value against time for each available year for a specific coin.

        Build one price-date line plot for each year available in the coin data. Assists in
        visualy identifying seasonal tendencies.

        Args:
            coin_id (str): Name of the coin to analyze
            date_col (str, optional): The name of the column representing the date.
            price_col (str, optional): The name of the column representing the price.
        """
        # Use train data, if not defined yet load from db
        if self.train_data is None:
            self.load_train_data()

        data = self.train_data

        # Extract coin data
        coin_data = data[data[COIN_ID] == coin_id]

        # Get available years
        years = coin_data[DATE].dt.year.unique()

        # Set the Seaborn style
        sns.set_theme(style="darkgrid")

        # Plot one line plot for every year
        _, ax = plt.subplots(figsize=(10, 6))

        for year in years:
            ax.plot(
                coin_data.loc[coin_data["date"].dt.year == year, COIN_PRICE]
                .squeeze()
                .reset_index(drop=True),
                label=year,
            )

        # Format the plot
        ax.set_title(f"{coin_id.title()} Comparative Yearly Price")
        ax.set_xlabel(f"{' '.join(date_col.title().split('_'))}")
        ax.set_ylabel(f"{' '.join(price_col.title().split('_'))}")
        plt.xticks(rotation=45)

        # Show legend
        ax.legend()

        # Show the plot
        plt.show()


class ARIMAModel(ForecastingModel):
    def __init__(self, coin_id: str):
        super().__init__()
        self.coin = coin_id
        self.fit_timestamp = None
        self.model = None

    def load_train_data(self, source: DataSources = DataSources.DATABASE, **kwargs):
        """Load historical data for the forecasting model.

        Passes arguments to parent class, then subsets data to the specific coin the child class
        is initialized with.

        Args:
            source (DataSources, optional): Passed to the parent class load_train_data method.
        """
        data = super().load_train_data(source, **kwargs)

        coin_data = data[data[COIN_ID] == self.coin]

        self.train_data = coin_data

        return coin_data

    def parallel_year_plot(self, date_col: str = DATE, price_col: str = COIN_PRICE):
        """Plots coin value against time for each available year.

        Applies parent class function with coin_id equals to child class coin_id.

        Args:
            date_col (str, optional): Date column. Passed to parent class.
            price_col (str, optional): Price column. Passed to parent class.
        """
        super().parallel_year_plot(coin_id=self.coin, date_col=date_col, price_col=price_col)

    def visualize_arima_params(self, lags: int = 90, diffs: int = 7, price_col: str = COIN_PRICE):
        """Creates ACF, PACF and integration visualizations to help set ARIMA parameters.

        Args:
            lags (int, optional): Number of lags to plot.
            diffs (int, optional): Number of diff time series to plot.
            price_col (str, optional): The name of the column representing the price.
        """
        # # Find parameters for ARIMA model
        # Find optimal diff for ARIMA
        dfuller_results = []

        # Run dfuller for the original time series
        dfuller_results.append(adfuller(self.train_data[price_col])[1])

        # Run dfuller for lagged time series
        for k in range(1, diffs):
            diff = self.train_data[price_col].diff(periods=k).iloc[k:]
            dfuller_p = adfuller(diff)[1]
            dfuller_results.append(dfuller_p)

        optimal_diff = dfuller_results.index(min(dfuller_results))

        if optimal_diff == 0:
            diff = self.train_data[price_col]
        else:
            diff = self.train_data[price_col].diff(periods=optimal_diff).iloc[optimal_diff:]

        _, ax = plt.subplots(1, 1, figsize=(10, 6))
        plt.plot(diff)
        ax.set_title(f"{optimal_diff} order differences for coin price series")

        # Plot ACF and PACF
        # Find the number of observations by taking the length of the returns DataFrame
        nobs = len(diff)

        # Compute the approximate confidence interval
        conf = 1.96 / sqrt(nobs)
        print("The approximate confidence interval is +/- %4.2f" % (conf))

        # Plot the acf and pacf functions with 95% confidence intervals
        plot_acf(diff, alpha=0.05, lags=lags)
        plot_pacf(diff, alpha=0.05, lags=lags)

    def fit(
        self,
        order: tuple[int, int, int] = ARIMA_DEAFULT_ORDER,
        seasonal_order: tuple[int, int, int, int] = (0, 0, 0, 0),
        exog: ArrayLike | None = None,
        evaluate: bool = False,
        train_test_split: float = 0.2,
        alpha: float = 0.05,
    ) -> SARIMAXResultsWrapper:
        """Fits an ARIMA model for the coin_id with the current train data.

        Args:
            order (tuple[int, int, int], Optional): Order for the ARIMA model.
            seasonal_order (tuple[int, int, int, int], optional): Seasonal order for the ARIMA
                model. Defaults to (0, 0, 0, 0).
            exog (ArrayLike | None, optional): Exogenous variables. Defaults to None.
            evaluate (bool, optional): If True a train test split is performed and results over this
                split are plotted. Otherwise the model is trained on the whole dataset. Defaults to
                False.
            train_test_split (float, optional): Fraction of data to keep for test. Defaults to 0.2.
            alpha (float, optional): Alpha for confidence interval plotting. Defaults to 0.05.

        Returns:
            SARIMAXResultsWrapper: A statsmodels trained ARIMA model.
        """
        # Get time series data
        if self.train_data is None:
            self.load_train_data()

        X = self.train_data[COIN_PRICE].values

        # Set exogenous training variables to constant if no exog variables
        if not exog:
            exog = np.ones(len(X))

        if evaluate:
            # Split train test
            test_size = int(len(X) * train_test_split)
            size = len(X) - test_size

            X_train, X_test = X[0:size], X[size : len(X)]
            exog_train, exog_test = exog[:size], exog[size:]

            # Train and forecast test
            model = SARIMAX(X_train, exog_train, order=order, seasonal_order=seasonal_order)
            model_fit = model.fit()
            model_fit.summary()

            fcast_test = model_fit.get_forecast(test_size, exog=exog_test)
            predictions_test = list(fcast_test.predicted_mean)

            # Evaluate
            rmse = sqrt(mean_squared_error(X_test, predictions_test))
            pct_error = rmse / (X_test.mean())
            print(
                "RMSE for test data:", rmse, "Average pct error for test data:", pct_error, sep="\n"
            )

            # Confidence intervals
            pred_conf_int_test = fcast_test.conf_int(alpha=alpha)
            lower_conf_test = list(pred_conf_int_test[:, 0])
            upper_conf_test = list(pred_conf_int_test[:, 1])

            # Plot predictions
            # Create x-axis values
            x_train_ax = np.arange(len(X_train))
            x_test_ax = np.arange(len(X_train), len(X_train) + len(X_test))

            _, ax = plt.subplots(1, 1, figsize=(10, 6))
            ax.plot(
                x_train_ax,
                X_train,
                color="black",
                linewidth=3,
                marker=".",
                markersize=5,
                label="Train",
            )
            ax.plot(
                x_test_ax,
                X_test,
                color="green",
                linewidth=3,
                marker=".",
                markersize=5,
                label="Test",
            )
            ax.plot(
                x_test_ax,
                predictions_test,
                color="blue",
                linewidth=3,
                marker=".",
                markersize=5,
                label="Predict",
            )
            ax.plot(
                x_test_ax,
                lower_conf_test,
                color="blue",
                linestyle="dashed",
                label=f"{(1-alpha)*100}% confidence interval",
            )
            ax.plot(x_test_ax, upper_conf_test, color="blue", linestyle="dashed")
            ax.legend()
            plt.ylim(0, 1.3 * max(upper_conf_test))
            plt.show()

        # Re train with full data
        model = SARIMAX(X, exog, order=order, seasonal_order=seasonal_order)
        model_fit = model.fit()

        self.fit_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.model = model_fit

        # Save instance of class with trained model in historic models dir
        model_name = (
            f"{self.coin}_ARIMA_{'.'.join(list([str(o) for o in order]))}_"
            f"{'.'.join(list([str(o) for o in seasonal_order]))}"
        )
        history_path = MODELS_FORECASTING_HISTORY / (model_name + f"_{self.fit_timestamp}.pickle")
        logger.info(f"Model saved to {history_path}")

        with history_path.open("wb") as file:
            pickle.dump(self, file)

        # Symlink to current model dir
        current_path = MODELS_FORECASTING / (model_name + "_latest.pickle")
        current_path.unlink(missing_ok=True)
        current_path.symlink_to(history_path)

        return model_fit

    def forecast(self, target_date: datetime.date) -> Mapping[datetime.date, float]:
        """Generates coin price forecasts for every date until given target_date.

        Args:
            target_date (datetime.date): Target date to predict.

        Raises:
            ValueError: Model must be trained prior to forecast.
            ValueError: Target date must be greater than train date.

        Returns:
            Mapping[datetime.date, float]: A Mapping from date to price prediction for range of
                dates from fitted day plus one to target date.
        """
        # Use latest date in the train data as starting point for forecast
        if self.model:
            start_date = self.train_data[DATE].max().date()
            logger.info(f"Model is trained with data until {start_date}")
        else:
            raise ValueError("Model needs to be fitted before forecasting.")

        # Sanity checks
        if target_date <= start_date:
            raise ValueError("Target date must be greater than fit date")

        # Forecast coin prices for dates from start_date to target_date
        num_forecast_days = (target_date - start_date).days
        date_range = [
            start_date + datetime.timedelta(days=i) for i in range(1, num_forecast_days + 1)
        ]

        forecasted_prices = self.model.get_forecast(
            # TODO: Add logic for exog management
            num_forecast_days,
            exog=[1] * num_forecast_days,
        ).predicted_mean

        return {date: forecast for date, forecast in zip(date_range, forecasted_prices)}
