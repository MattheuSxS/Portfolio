import logging
import pandas as pd
from datetime import date

try:
    from .bigquery import BigQuery
    from .save_all_models import ModelSaver
    from .prophet_model import ProphetModel
    from .holtwinters_model import HoltWintersModel
except ImportError:
    from bigquery import BigQuery
    from save_all_models import ModelSaver
    from prophet_model import ProphetModel
    from holtwinters_model import HoltWintersModel


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)



class ForecastingHelper(BigQuery):
    """
    A helper class for running forecasting models on time series data.

    Attributes:
        df (pd.DataFrame): The input DataFrame containing time series data.
        model_type (str): The type of forecasting model to use ('prophet' or 'holtwinters').
        horizon (int): The forecast horizon in days.
        n_cutoffs (int): The number of cutoff dates to generate for cross-validation.

    Methods:
        generate_cutoffs(): Generate a list of cutoff dates for time series forecasting.
        run_forecasting(): Run the specified forecasting model and return the results.
    """

    def __init__(self, project: str, horizon: int = 28, n_cutoffs: int = 3) -> None:
        super().__init__(project=project)

        self.horizon = horizon
        self.n_cutoffs = n_cutoffs
        self.df = self.get_data_from_bigquery(
            query = f"""
                        SELECT
                            FORMAT_DATE('%Y-%m-%d', purchase_date) AS ds,
                            ROUND(SUM(final_price), 2) AS y
                        FROM
                            `{project}.ls_customers.tb_sales`
                        GROUP BY
                            ALL
                        QUALIFY
                            ROW_NUMBER() OVER (ORDER BY y) > 2 AND ROW_NUMBER() OVER (ORDER BY y DESC) > 2
                        ORDER BY
                            y;
            """
        )

        self.df["ds"] = pd.to_datetime(self.df["ds"])


    def generate_cutoffs(self) -> list:
        """Generate a list of cutoff dates for time series forecasting."""
        max_date = self.df["ds"].max()
        last_cutoff = max_date - pd.Timedelta(days=self.horizon)

        cutoffs = pd.date_range(
            end     = last_cutoff,
            periods = self.n_cutoffs,
            freq    = "14D"
        )

        return cutoffs.tolist()


    def run_forecasting(self) -> dict:
        """Run both forecasting models and return their results."""

        cutoffs = self.generate_cutoffs()

        forecast_end = f"{date.today().year}-12-31"

        prophet_result = ProphetModel(
            self.df
        ).run(
            cutoffs = cutoffs,
            forecast_end = forecast_end
        )

        holt_winters_result = HoltWintersModel(
            self.df
        ).run(
            cutoffs = cutoffs,
            forecast_end = forecast_end
        )

        return {
            "prophet": prophet_result,
            "holt_winters": holt_winters_result
        }

    def combine_forecasts(self) -> pd.DataFrame:
        """Combine actuals, historical predictions and future forecasts."""

        result = self.run_forecasting()

        actual = self.df[["ds", "y"]].rename(
            columns={"y": "actual"}
        )

        prophet_historical = (
            result["prophet"]["historical"]
            .rename(columns={"yhat": "prophet"})
        )

        prophet_future = (
            result["prophet"]["forecast"][["ds", "yhat"]]
            .rename(columns={"yhat": "prophet"})
        )

        holt_historical = (
            result["holt_winters"]["historical"]
            .rename(columns={"yhat": "holt_winters"})
        )

        holt_future = (
            result["holt_winters"]["forecast"][["ds", "yhat"]]
            .rename(columns={"yhat": "holt_winters"})
        )

        logging.info("Combining actuals, historical predictions and future forecasts...")
        prophet = pd.concat(
            [
                prophet_historical,
                prophet_future
            ],
            ignore_index=True
        )

        holt_winters = pd.concat(
            [
                holt_historical,
                holt_future
            ],
            ignore_index=True
        )

        forecast_df = (
            actual.merge(
                prophet,
                on = "ds",
                how = "outer"
            )
            .merge(
                holt_winters,
                on = "ds",
                how = "outer"
            )
            .sort_values("ds")
            .reset_index(drop=True)
        )


        return [forecast_df, result]

    def run_all(self) -> None:
        """Run the entire forecasting process and return the combined forecast DataFrame and results."""

        forecast_df, result = self.combine_forecasts()

        logging.info("Saving models and metadata to disk...")
        try:
            ModelSaver(
                df = self.df,
                result = result,
                dataset_name = "sales_forecast"
            ).save_models()
        except Exception as e:
            logging.warning(f"Failed to save models: {e}")

        logging.info("Sending combined forecasts to BigQuery...")


        self.batch_load_from_memory(
            data = forecast_df,
            dataset = "production",
            table = "tb_sales_forecast"
        )

        logging.info("Forecasting process completed successfully.")


if __name__ == "__main__":
    project = "gcp-mts-pf"
    helper = ForecastingHelper(project=project)
    helper.run_all()