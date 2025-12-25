# ******************************************************************************************************************** #
#                                                Main Function                                                         #
# ******************************************************************************************************************** #
def get_schema_from_bigquery(project_id: str, dataset_id: str, table_id: str) -> str:
    import logging
    from google.cloud import bigquery

    try:
        client = bigquery.Client(project=project_id)
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        table = client.get_table(table_ref)

        field_types = [f"{field.name}:{field.field_type}" for field in table.schema]

        return ", ".join(field_types)
    except Exception as e:
        logging.error(f"❌ Error getting BigQuery schema: {e}")
        raise
