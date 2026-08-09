import logging
import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error
)


class ProphetModel:
    """Prophet Model for Time Series Forecasting"""
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def train(self) -> Prophet:
        """_summary_"""
        model = Prophet(
            weekly_seasonality  = True,
            daily_seasonality   = False,
            yearly_seasonality  = False
        )

        model.fit(self.df[["ds", "y"]])

        return model

    def generate_forecast(self, model: Prophet, forecast_end: str) -> pd.DataFrame:
        """_summary_"""
        training_end = self.df["ds"].max()

        future_dates = pd.date_range(
            start   = training_end + pd.Timedelta(days=1),
            end     = forecast_end,
            freq    = "D"
        )

        future = pd.DataFrame({
            "ds": future_dates
        })

        forecast = model.predict(future)

        return forecast[
            ["ds", "yhat", "yhat_lower", "yhat_upper"]
        ]

    def evaluate(self, cutoffs:any, horizon:int = 28) -> pd.DataFrame:
        """_summary_"""
        results = []

        for cutoff in cutoffs:

            train = self.df[self.df["ds"] <= cutoff].copy()

            test = self.df[
                (self.df["ds"] > cutoff) &
                (
                    self.df["ds"]
                    <= cutoff + pd.Timedelta(days=horizon)
                )
            ].copy()

            model = Prophet(
                weekly_seasonality  = True,
                daily_seasonality   = False,
                yearly_seasonality  = False
            )

            model.fit(train[["ds", "y"]])

            forecast = model.predict(test[["ds"]])

            y_true = test["y"].to_numpy()
            y_pred = forecast["yhat"].to_numpy()

            results.append({
                "cutoff": cutoff,
                "MAE": mean_absolute_error(
                    y_true,
                    y_pred
                ),
                "RMSE": np.sqrt(
                    mean_squared_error(
                        y_true,
                        y_pred
                    )
                ),
                "MAPE": mean_absolute_percentage_error(
                    y_true,
                    y_pred
                )
            })

        return pd.DataFrame(results)


    def generate_historical_forecast(self, model: Prophet) -> pd.DataFrame:
        """Generate predictions for the historical period."""

        forecast = model.predict(self.df[["ds"]])

        return forecast[["ds", "yhat"]]


    def run(self, cutoffs: any, forecast_end: str) -> dict:

        model = self.train()

        metrics = self.evaluate(cutoffs=cutoffs)

        historical = self.generate_historical_forecast(
            model = model
        )

        forecast = self.generate_forecast(
            model = model,
            forecast_end = forecast_end
        )

        return {
            "model": model,
            "metrics": metrics,
            "historical": historical,
            "forecast": forecast
        }