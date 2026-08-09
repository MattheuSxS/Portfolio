import logging
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error
)


class HoltWintersModel:
    """Holt-Winters Model for Time Series Forecasting"""
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def train(self):
        """"""
        model = ExponentialSmoothing(
            endog                   = self.df["y"],
            trend                   = None,
            seasonal                = "add",
            seasonal_periods        = 7,
            initialization_method   = "estimated"
        )

        fitted_model = model.fit(
            optimized = True
        )

        return fitted_model

    def generate_forecast(self, model: ExponentialSmoothing, forecast_end: str) -> pd.DataFrame:
        """"""
        training_end = self.df["ds"].max()

        future_dates = pd.date_range(
            start   = training_end + pd.Timedelta(days=1),
            end     = pd.Timestamp(forecast_end),
            freq    = "D"
        )

        forecast = model.forecast(len(future_dates))

        return pd.DataFrame({
            "ds": future_dates,
            "yhat": forecast.to_numpy()
        })

    def evaluate(self, cutoffs: any, horizon: int = 28) -> pd.DataFrame:
        """"""
        results = []

        for cutoff in cutoffs:

            train = self.df[
                self.df["ds"] <= cutoff
            ].copy()

            test = self.df[
                (self.df["ds"] > cutoff) &
                (
                    self.df["ds"]
                    <= cutoff + pd.Timedelta(days=horizon)
                )
            ].copy()

            model = ExponentialSmoothing(
                train["y"],
                trend=None,
                seasonal="add",
                seasonal_periods=7,
                initialization_method="estimated"
            )

            fitted_model = model.fit(
                optimized=True
            )

            forecast = fitted_model.forecast(
                len(test)
            )

            y_true = test["y"].to_numpy()
            y_pred = forecast.to_numpy()

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

    def generate_historical_forecast( self,  model: ExponentialSmoothing) -> pd.DataFrame:
        """Generate predictions for the historical period."""

        fitted = model.fittedvalues

        return pd.DataFrame({
            "ds": self.df["ds"].to_numpy(),
            "yhat": fitted.to_numpy()
        })


    def run(self, cutoffs: any, forecast_end : str) -> dict:

        model = self.train()

        metrics = self.evaluate(cutoffs=cutoffs)

        historical = self.generate_historical_forecast(model=model)

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