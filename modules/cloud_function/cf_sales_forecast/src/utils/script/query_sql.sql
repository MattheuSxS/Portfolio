WITH sales_dates AS (
  SELECT DISTINCT
    TIMESTAMP_TRUNC(purchase_date, DAY) AS purchase_date
  FROM
    `gcp-mts-pf.ls_customers.tb_sales`
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
    `gcp-mts-pf.ls_customers.tb_sales` AS TBSS
  INNER JOIN
    `gcp-mts-pf.ls_customers.tb_address` AS TBAS
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
  ON sales.purchase_date = valid_dates.purchase_date
WHERE
  valid_dates.rn_asc > 2
  AND valid_dates.rn_desc > 2
ORDER BY
  sales.state,
  sales.purchase_date;