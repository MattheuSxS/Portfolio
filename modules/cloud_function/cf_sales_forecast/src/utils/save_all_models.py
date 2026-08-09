import json
import joblib
import pandas as pd
from pathlib import Path


class ModelSaver:
    """Class to save trained models and metadata."""
    def __init__(self, df: pd.DataFrame, result: dict, dataset_name: str, model_dir: str = None):
        self.result = result
        self.df = df
        self.dataset_name = dataset_name
        self.model_dir = "modules/cloud_function/cf_sales_forecast/src/models" if model_dir is None else model_dir

    def save_models(self) -> dict:
        """Save trained models and metadata to disk."""

        model_dir = Path(self.model_dir)
        model_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        prophet_path = (
            model_dir /
            f"{self.dataset_name}_prophet.pkl"
        )

        holt_winters_path = (
            model_dir /
            f"{self.dataset_name}_holt_winters.pkl"
        )

        metadata_path = (
            model_dir /
            f"{self.dataset_name}_metadata.json"
        )

        joblib.dump(
            self.result["prophet"]["model"],
            prophet_path
        )

        joblib.dump(
            self.result["holt_winters"]["model"],
            holt_winters_path
        )

        metadata = {
            "dataset": self.dataset_name,

            "training_start": (
                self.df["ds"]
                .min()
                .strftime("%Y-%m-%d")
            ),

            "training_end": (
                self.df["ds"]
                .max()
                .strftime("%Y-%m-%d")
            ),

            "forecast_start": (
                self.result["prophet"]["forecast"]["ds"]
                .min()
                .strftime("%Y-%m-%d")
            ),

            "forecast_end": (
                self.result["prophet"]["forecast"]["ds"]
                .max()
                .strftime("%Y-%m-%d")
            ),

            "models": {
                "prophet": {
                    "weekly_seasonality": True,
                    "daily_seasonality": False,
                    "yearly_seasonality": False
                },

                "holt_winters": {
                    "trend": None,
                    "seasonal": "add",
                    "seasonal_periods": 7
                }
            },

            "metrics": {
                "prophet": {
                    "mae": float(
                        self.result["prophet"]["metrics"]["MAE"].mean()
                    ),
                    "rmse": float(
                        self.result["prophet"]["metrics"]["RMSE"].mean()
                    ),
                    "mape": float(
                        self.result["prophet"]["metrics"]["MAPE"].mean()
                    )
                },

                "holt_winters": {
                    "mae": float(
                        self.result["holt_winters"]["metrics"]["MAE"].mean()
                    ),
                    "rmse": float(
                        self.result["holt_winters"]["metrics"]["RMSE"].mean()
                    ),
                    "mape": float(
                        self.result["holt_winters"]["metrics"]["MAPE"].mean()
                    )
                }
            }
        }

        with open(file = metadata_path, mode = "w") as file:
            json.dump(metadata, file, indent = 4)

        return {
            "prophet": str(prophet_path),
            "holt_winters": str(holt_winters_path),
            "metadata": str(metadata_path)
        }
