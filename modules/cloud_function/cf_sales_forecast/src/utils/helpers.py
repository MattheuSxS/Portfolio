import logging
import pandas as pd
from datetime import date

try:
    from .bigquery import BigQuery
except ImportError:
    from bigquery import BigQuery

try:
    from .prophet_model import ProphetModel
except ImportError:
    from prophet_model import ProphetModel

try:
    from .holtwinters_model import HoltWintersModel
except ImportError:
    from holtwinters_model import HoltWintersModel

try:
    from .save_all_models import ModelSaver
except ImportError:
    from save_all_models import ModelSaver


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

    def __init__(self, project: str, dataset: str, table: list, horizon: int = 28, n_cutoffs: int = 3) -> None:
        super().__init__(project=project)

        self.project    = project
        self.dataset    = dataset
        self.table      = table
        self.horizon    = horizon
        self.n_cutoffs  = n_cutoffs
        self.sql_query  = {
            "get_sales_data": \
                f"""
                    WITH sales_dates AS (
                        SELECT DISTINCT
                            TIMESTAMP_TRUNC(purchase_date, DAY) AS purchase_date
                        FROM
                            `{self.project}.{self.dataset[0]}.{self.table[0]}`
                        WHERE
                            order_status = "completed"
                    ),
                    valid_dates AS (
                        SELECT
                            purchase_date,
                            ROW_NUMBER() OVER (ORDER BY purchase_date) AS rn_asc,
                            ROW_NUMBER() OVER (ORDER BY purchase_date DESC) AS rn_desc
                        FROM
                            sales_dates
                    ),
                    sales AS (
                        SELECT
                            TIMESTAMP_TRUNC(TBSS.purchase_date, DAY) AS purchase_date,
                            TBAS.state,
                            ROUND(SUM(TBSS.final_price), 2) AS y
                        FROM
                            `{self.project}.{self.dataset[0]}.{self.table[0]}` AS TBSS
                        INNER JOIN
                            `{self.project}.{self.dataset[0]}.{self.table[1]}` AS TBAS
                            ON TBSS.associate_id = TBAS.fk_associate_id
                        WHERE
                            TBSS.order_status = "completed"
                        GROUP BY
                            purchase_date,
                            TBAS.state
                    )
                    SELECT
                            FORMAT_TIMESTAMP('%Y-%m-%d', sales.purchase_date) AS ds,
                            sales.state,
                            sales.y
                    FROM
                        sales
                    INNER JOIN
                        valid_dates
                    ON
                        sales.purchase_date = valid_dates.purchase_date
                    WHERE
                        valid_dates.rn_asc > 2
                        AND valid_dates.rn_desc > 2
                    ORDER BY
                        sales.state,
                        sales.purchase_date;
                """,
            "query_ddl": \
                f"""
                    TRUNCATE TABLE `{self.project}.{self.dataset[1]}.{self.table[2]}`;
                """
        }
        self.df = self.get_data_from_bigquery(
            query = self.sql_query["get_sales_data"]
        )

        self.df["ds"] = pd.to_datetime(self.df["ds"])
        self.df_aggregated = self.df[["ds", "y"]].groupby("ds").agg({"y": "sum"}).reset_index()


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


    def run_forecasting(self, df: pd.DataFrame) -> dict:
        """Run both forecasting models and return their results."""

        cutoffs = self.generate_cutoffs()

        forecast_end = f"{date.today().year}-12-31"

        prophet_result = ProphetModel(
            df
        ).run(
            cutoffs = cutoffs,
            forecast_end = forecast_end
        )

        holt_winters_result = HoltWintersModel(
            df
        ).run(
            cutoffs = cutoffs,
            forecast_end = forecast_end
        )

        return {
            "prophet": prophet_result,
            "holt_winters": holt_winters_result
        }

    def combine_forecasts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combine actuals, historical predictions and future forecasts."""

        result = self.run_forecasting(df)

        actual = df[["ds", "y"]].rename(
            columns = {"y": "actual"}
        )

        prophet_historical = (
            result["prophet"]["historical"]
            .rename(columns = {"yhat": "prophet"})
        )

        prophet_future = (
            result["prophet"]["forecast"][["ds", "yhat"]]
            .rename(columns = {"yhat": "prophet"})
        )

        holt_historical = (
            result["holt_winters"]["historical"]
            .rename(columns = {"yhat": "holt_winters"})
        )

        holt_future = (
            result["holt_winters"]["forecast"][["ds", "yhat"]]
            .rename(columns = {"yhat": "holt_winters"})
        )

        logging.info("Combining actuals, historical predictions and future forecasts...")
        prophet = pd.concat(
            [
                prophet_historical,
                prophet_future
            ],
            ignore_index = True
        )

        holt_winters = pd.concat(
            [
                holt_historical,
                holt_future
            ],
            ignore_index = True
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
            .reset_index(drop = True)
        )


        return [forecast_df, result]

    def run_all(self) -> None:
        """
        """

        state_list = self.df["state"].unique().tolist()
        df_list = pd.DataFrame({
            "ds": [],
            "actual": [],
            "prophet": [],
            "holt_winters": [],
            "state": [],
        })

        try:
            for state in state_list:
                logging.info(f"Running forecasting for state: {state}...")
                state_df = self.df[self.df["state"] == state].copy()
                forecast_df, result = self.combine_forecasts(state_df)
                forecast_df["state"] = state

                df_list = pd.concat([df_list, forecast_df], ignore_index=True)

                try:
                    ModelSaver(
                        df = forecast_df,
                        result = result,
                        dataset_name = f"{state}_sales_forecast"
                    ).save_models()

                except Exception as e:
                    logging.warning(f"Failed to save models: {e}")

            logging.info("Truncating the target table in BigQuery...")
            self.execute_ddl(
                query = self.sql_query["query_ddl"]
            )

        except Exception as e:
            logging.error(f"Error during forecasting process: {e}")
            raise

        logging.info(f"Sending combined forecasts to BigQuery for state: {state}...")
        self.batch_load_from_memory(
            data    = df_list,
            dataset = self.dataset[1],
            table   = self.table[2]
        )

if __name__ == "__main__":
    project = "gcp-mts-pf"
    helper = \
        ForecastingHelper(
            project = project,
            dataset = ["ls_customers", "production"],
            table   = ["tb_sales", "tb_address", "tb_sales_forecast"]
        )
    helper.run_all()